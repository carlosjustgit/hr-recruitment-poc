"""
Advanced HR Demo with Google Sheets and PhantomBuster integration
"""
import streamlit as st
import pandas as pd
import os
import requests
import json
from datetime import datetime
import time
import traceback

# Import service modules
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set page config
st.set_page_config(page_title="Chile HR Demo", page_icon="🇨🇱", layout="wide")

# Configuration
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "3192622034872375"

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'do_search' not in st.session_state:
    st.session_state.do_search = False
if 'candidates' not in st.session_state:
    st.session_state.candidates = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'phantom_job_id' not in st.session_state:
    st.session_state.phantom_job_id = None
if 'phantom_status' not in st.session_state:
    st.session_state.phantom_status = None

# Title and description
st.title("🇨🇱 Chile HR Demo")
st.markdown("Search for candidates in Chile using natural language")

# Warning banner
st.warning("⚠️ **PROOF OF CONCEPT**: This is a demo to showcase the user experience. In production, data sources will be official and consented.")

# Functions to interact with Google Sheets
def get_sheet_data():
    """Get data from Google Sheet"""
    try:
        # Check if credentials file exists
        if not os.path.exists("service-account-key.json"):
            st.error("Service account key file not found")
            return []
            
        # Setup credentials
        credentials = Credentials.from_service_account_file(
            "service-account-key.json",
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        # Get data from sheet
        sheet_range = "candidatos!A1:Z"
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=sheet_range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            st.warning("No data found in sheet")
            return []
            
        # Convert to list of dicts
        headers = values[0]
        candidates = []
        
        for row in values[1:]:
            # Ensure row is same length as headers
            while len(row) < len(headers):
                row.append("")
                
            candidate = {}
            for i, header in enumerate(headers):
                candidate[header] = row[i]
                
            candidates.append(candidate)
            
        st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.data_loaded = True
        return candidates
        
    except Exception as e:
        st.error(f"Error loading sheet data: {e}")
        traceback.print_exc()
        return []

# Functions to interact with PhantomBuster
def launch_phantom_job(query="Chile AND (finanzas OR marketing OR ingeniería)", limit=5):
    """Launch PhantomBuster job"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/launch"
        
        # Payload for PhantomBuster
        payload = {
            "id": PHANTOM_AGENT_ID,
            "argument": {
                "spreadsheetId": SHEET_ID,
                "numberOfProfiles": limit,
                "searchQuery": query,
                "sessionCookie": ""
            }
        }
        
        headers = {
            "X-Phantombuster-Key": PHANTOM_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("containerId")
            st.session_state.phantom_job_id = job_id
            st.session_state.phantom_status = "running"
            return job_id
        else:
            st.error(f"Error launching PhantomBuster job: {response.status_code}")
            st.session_state.phantom_status = "error"
            return None
            
    except Exception as e:
        st.error(f"Error launching PhantomBuster job: {e}")
        st.session_state.phantom_status = "error"
        return None

def check_phantom_status(job_id):
    """Check PhantomBuster job status"""
    try:
        url = f"https://api.phantombuster.com/api/v2/containers/fetch-output"
        
        headers = {
            "X-Phantombuster-Key": PHANTOM_API_KEY
        }
        
        params = {"id": job_id}
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            
            if status == "finished":
                st.session_state.phantom_status = "completed"
                return "completed"
            elif status == "error":
                st.session_state.phantom_status = "error"
                return "error"
            else:
                return "running"
        else:
            return "unknown"
            
    except Exception as e:
        st.error(f"Error checking PhantomBuster status: {e}")
        return "error"

# Sidebar
with st.sidebar:
    st.header("Data Controls")
    
    # Update data section
    st.subheader("🔄 Update Data")
    
    update_col1, update_col2 = st.columns([3,1])
    
    with update_col1:
        update_button = st.button("Update from Sheet", key="update_sheet")
    
    with update_col2:
        phantom_button = st.button("🤖", help="Run PhantomBuster to get new data")
    
    # Show phantom status if job is running
    if st.session_state.phantom_status == "running" and st.session_state.phantom_job_id:
        with st.spinner("PhantomBuster job running..."):
            status = check_phantom_status(st.session_state.phantom_job_id)
            if status == "completed":
                st.success("PhantomBuster job completed!")
                # Refresh data
                st.session_state.candidates = get_sheet_data()
            elif status == "error":
                st.error("PhantomBuster job failed")
    
    # Show last update time
    if st.session_state.last_update:
        st.caption(f"Last updated: {st.session_state.last_update}")
    
    # Metrics
    st.subheader("📊 Metrics")
    
    metrics_col1, metrics_col2 = st.columns(2)
    
    with metrics_col1:
        st.metric("Candidates", len(st.session_state.candidates) if st.session_state.data_loaded else 0)
    
    with metrics_col2:
        st.metric("Status", "Active" if st.session_state.data_loaded else "Inactive")

# Handle button actions
if update_button:
    with st.spinner("Loading data from Google Sheet..."):
        st.session_state.candidates = get_sheet_data()
        st.success(f"Loaded {len(st.session_state.candidates)} candidates from sheet")

if phantom_button:
    with st.spinner("Launching PhantomBuster job..."):
        job_id = launch_phantom_job()
        if job_id:
            st.success(f"PhantomBuster job launched! ID: {job_id}")
        else:
            st.error("Failed to launch PhantomBuster job")

# Main area - Search
st.header("🔍 Search Candidates")

# Function to set search query and trigger search
def set_search_query(query_text):
    st.session_state.search_query = query_text
    st.session_state.do_search = True

# Search box
query = st.text_input("Search:", placeholder="Example: Quien tiene magíster en finanzas?", 
                     value=st.session_state.search_query if st.session_state.search_query else "")

# Update query from session state if needed
if st.session_state.search_query and not query:
    query = st.session_state.search_query
    # Clear the session state to avoid infinite loop
    st.session_state.search_query = ""

# Search suggestions
if not query:
    st.info("Try these searches:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Quien tiene magíster en finanzas?", key="btn1"):
            set_search_query("Quien tiene magíster en finanzas?")
            st.rerun()
        if st.button("Quien trabajó en marketing digital?", key="btn2"):
            set_search_query("Quien trabajó en marketing digital?")
            st.rerun()
        if st.button("Quien tiene experiencia en minería?", key="btn3"):
            set_search_query("Quien tiene experiencia en minería?")
            st.rerun()
    
    with col2:
        if st.button("Quien tiene experiencia en análisis de riesgo?", key="btn4"):
            set_search_query("Quien tiene experiencia en análisis de riesgo?")
            st.rerun()
        if st.button("Quien tiene skills en Python y data science?", key="btn5"):
            set_search_query("Quien tiene skills en Python y data science?")
            st.rerun()
        if st.button("Quien trabajó en startups chilenas?", key="btn6"):
            set_search_query("Quien trabajó en startups chilenas?")
            st.rerun()

# Show results if query or search button is clicked
if query or st.button("Search") or st.session_state.do_search:
    # Reset search flag
    st.session_state.do_search = False
    
    with st.spinner("Searching..."):
        # Display the search query
        search_term = query or "your search"
        
        # Use real data if available, otherwise use demo data
        if st.session_state.data_loaded and st.session_state.candidates:
            candidates = st.session_state.candidates
        else:
            # Demo data
            candidates = [
                {
                    'name': 'Carlos Mendoza',
                    'headline': 'Analista Financiero Senior',
                    'location': 'Santiago, Chile',
                    'current_company': 'Banco Santander Chile',
                    'education': 'Magíster en Finanzas - Universidad de Chile',
                    'linkedin_url': 'https://linkedin.com/in/carlos-mendoza',
                    'skills_tags': 'finanzas, análisis'
                },
                {
                    'name': 'María González',
                    'headline': 'Marketing Manager Digital',
                    'location': 'Valparaíso, Chile',
                    'current_company': 'StartupTech Chile',
                    'education': 'Ingeniería Comercial - PUCV',
                    'linkedin_url': 'https://linkedin.com/in/maria-gonzalez',
                    'skills_tags': 'marketing, digital'
                },
                {
                    'name': 'Diego Ramírez',
                    'headline': 'Data Scientist',
                    'location': 'Concepción, Chile',
                    'current_company': 'TechCorp Chile',
                    'education': 'Ingeniería Informática - Universidad de Concepción',
                    'linkedin_url': 'https://linkedin.com/in/diego-ramirez',
                    'skills_tags': 'tecnología, análisis'
                },
                {
                    'name': 'Ana Herrera',
                    'headline': 'Contadora Senior',
                    'location': 'Santiago, Chile',
                    'current_company': 'EY Chile',
                    'education': 'Contador Auditor - Universidad de Chile',
                    'linkedin_url': 'https://linkedin.com/in/ana-herrera',
                    'skills_tags': 'contabilidad, auditoría'
                },
                {
                    'name': 'Roberto Silva',
                    'headline': 'Ingeniero de Ventas',
                    'location': 'Antofagasta, Chile',
                    'current_company': 'Minera Escondida',
                    'education': 'Ingeniería Industrial - Universidad Católica del Norte',
                    'linkedin_url': 'https://linkedin.com/in/roberto-silva',
                    'skills_tags': 'ventas, minería'
                }
            ]
        
        # Filter results based on search query
        filtered_candidates = []
        search_term_lower = search_term.lower()
        
        # Simple filtering logic based on the search term
        for candidate in candidates:
            score = 0
            
            # Check various fields for matches
            if "magíster" in search_term_lower and "magíster" in candidate.get('education', '').lower():
                score += 3
            if "finanzas" in search_term_lower and "finanzas" in candidate.get('skills_tags', '').lower():
                score += 2
            if "marketing" in search_term_lower and "marketing" in candidate.get('skills_tags', '').lower():
                score += 2
            if "digital" in search_term_lower and "digital" in candidate.get('skills_tags', '').lower():
                score += 1
            if "minería" in search_term_lower and "minería" in candidate.get('skills_tags', '').lower():
                score += 2
            if "análisis" in search_term_lower and "análisis" in candidate.get('skills_tags', '').lower():
                score += 2
            if "riesgo" in search_term_lower and "riesgo" in candidate.get('skills_tags', '').lower():
                score += 1
            if "python" in search_term_lower and "tecnología" in candidate.get('skills_tags', '').lower():
                score += 2
            if "data science" in search_term_lower and "tecnología" in candidate.get('skills_tags', '').lower():
                score += 2
            if "startups" in search_term_lower and "startup" in candidate.get('current_company', '').lower():
                score += 2
                
            if score > 0:
                candidate['match_score'] = score
                filtered_candidates.append(candidate)
        
        # Sort by match score
        filtered_candidates.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # If no matches, show all candidates
        if not filtered_candidates:
            filtered_candidates = candidates
            for candidate in filtered_candidates:
                candidate['match_score'] = 1
        
        # Display results
        st.success(f"Found {len(filtered_candidates)} candidates matching '{search_term}'")
        
        # Results
        for i, candidate in enumerate(filtered_candidates[:5]):  # Show top 5
            score = candidate.get('match_score', 1)
            match_percentage = min(int(score * 20), 95)  # Convert score to percentage, max 95%
            
            with st.expander(f"{candidate.get('name', 'Unknown')} - {candidate.get('headline', 'No headline')}"):
                col1, col2 = st.columns([2,1])
                
                with col1:
                    st.write(f"**Company:** {candidate.get('current_company', 'N/A')}")
                    st.write(f"**Education:** {candidate.get('education', 'N/A')}")
                    st.write(f"**Location:** {candidate.get('location', 'N/A')}")
                    st.write(f"**Skills:** {candidate.get('skills_tags', 'N/A')}")
                
                with col2:
                    st.write(f"**Match:** {match_percentage}%")
                    
                    # Relevance indicator based on score
                    if score >= 4:
                        st.write("**Relevance:** High")
                    elif score >= 2:
                        st.write("**Relevance:** Medium")
                    else:
                        st.write("**Relevance:** Low")
                    
                    # LinkedIn link
                    linkedin_url = candidate.get('linkedin_url', '')
                    if linkedin_url:
                        st.markdown(f"[View LinkedIn]({linkedin_url})")
                    
                    # Google Sheet link
                    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
                    st.markdown(f"[View in Sheet]({sheet_url})")

# Footer
st.divider()
st.caption(f"Demo HR Agent - Chile Edition | {datetime.now().strftime('%Y-%m-%d')}")

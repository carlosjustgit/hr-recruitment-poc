"""
Practical PoC for HR Recruitment Agent
- Upload contacts
- Add to main spreadsheet
- Enrich via PhantomBuster
- Query enriched data
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import json
import time
from datetime import datetime
import traceback
import io

# Import service modules
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set page config
st.set_page_config(page_title="HR Recruitment PoC", page_icon="🔍", layout="wide")

# Configuration
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "3192622034872375"

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'candidates' not in st.session_state:
    st.session_state.candidates = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'phantom_job_id' not in st.session_state:
    st.session_state.phantom_job_id = None
if 'phantom_status' not in st.session_state:
    st.session_state.phantom_status = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

# Title and description
st.title("HR Recruitment Agent - PoC")
st.markdown("Upload contacts, enrich data, and search candidates using natural language")

# Warning banner
st.warning("⚠️ **PROOF OF CONCEPT**: This is a demo to showcase the functionality. In production, data sources will be official and consented.")

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

def write_to_sheet(data):
    """Write data to Google Sheet"""
    try:
        # Check if credentials file exists
        if not os.path.exists("service-account-key.json"):
            st.error("Service account key file not found")
            return False
            
        # Setup credentials
        credentials = Credentials.from_service_account_file(
            "service-account-key.json",
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        # Get existing data to determine headers
        sheet_range = "candidatos!A1:Z1"
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=sheet_range
        ).execute()
        
        existing_headers = result.get('values', [[]])[0]
        
        # If no headers exist, use the data headers
        if not existing_headers:
            headers = list(data[0].keys())
        else:
            headers = existing_headers
            
            # Add any missing headers from data
            for row in data:
                for key in row.keys():
                    if key not in headers:
                        headers.append(key)
        
        # Prepare data for writing
        values = [headers]
        for row in data:
            values.append([row.get(header, "") for header in headers])
        
        # Determine if we're updating or appending
        if not existing_headers:
            # Write headers and data
            body = {'values': values}
            service.spreadsheets().values().update(
                spreadsheetId=SHEET_ID,
                range="candidatos!A1",
                valueInputOption='RAW',
                body=body
            ).execute()
        else:
            # Append data only
            body = {'values': values[1:]}  # Skip headers
            service.spreadsheets().values().append(
                spreadsheetId=SHEET_ID,
                range="candidatos!A1",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
        
        return True
        
    except Exception as e:
        st.error(f"Error writing to sheet: {e}")
        traceback.print_exc()
        return False

# Functions to interact with PhantomBuster
def launch_phantom_job(urls=None, query=None, limit=5):
    """Launch PhantomBuster job"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/launch"
        
        # Determine which type of job to launch
        if urls:
            # Profile scraper with URLs
            payload = {
                "id": PHANTOM_AGENT_ID,
                "argument": {
                    "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
                    "columnName": "linkedin_url",
                    "numberOfProfiles": limit
                }
            }
        elif query:
            # Search query
            payload = {
                "id": PHANTOM_AGENT_ID,
                "argument": {
                    "spreadsheetId": SHEET_ID,
                    "numberOfProfiles": limit,
                    "searchQuery": query
                }
            }
        else:
            st.error("Either URLs or query must be provided")
            return None
        
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

# Function to process uploaded file
def process_uploaded_file(uploaded_file):
    """Process uploaded CSV or Excel file"""
    try:
        # Check file type
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload CSV or Excel file.")
            return None
        
        # Convert to list of dicts
        data = df.replace({np.nan: None}).to_dict('records')
        
        # Ensure required fields
        required_fields = ['name', 'linkedin_url']
        for field in required_fields:
            if field not in df.columns:
                st.error(f"Required field '{field}' not found in uploaded file.")
                return None
        
        return data
        
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
        traceback.print_exc()
        return None

# Main layout with tabs
tab1, tab2, tab3 = st.tabs(["Upload & Enrich", "Search Candidates", "Data View"])

# Tab 1: Upload & Enrich
with tab1:
    st.header("Upload Contacts & Enrich Data")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload contacts (CSV or Excel)", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Process uploaded file
        data = process_uploaded_file(uploaded_file)
        
        if data:
            st.session_state.uploaded_data = data
            st.success(f"Successfully processed {len(data)} contacts")
            
            # Preview data
            st.subheader("Preview")
            st.dataframe(pd.DataFrame(data).head(5))
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Add to Spreadsheet", disabled=st.session_state.uploaded_data is None):
            with st.spinner("Adding contacts to spreadsheet..."):
                success = write_to_sheet(st.session_state.uploaded_data)
                if success:
                    st.success("Contacts added to spreadsheet!")
                    # Refresh data
                    st.session_state.candidates = get_sheet_data()
                else:
                    st.error("Failed to add contacts to spreadsheet")
    
    with col2:
        if st.button("Enrich with PhantomBuster"):
            with st.spinner("Launching PhantomBuster job..."):
                job_id = launch_phantom_job(urls=True)
                if job_id:
                    st.success(f"PhantomBuster job launched! ID: {job_id}")
                else:
                    st.error("Failed to launch PhantomBuster job")
    
    with col3:
        if st.button("Load Current Data"):
            with st.spinner("Loading data from Google Sheet..."):
                st.session_state.candidates = get_sheet_data()
                st.success(f"Loaded {len(st.session_state.candidates)} candidates from sheet")
    
    # Show phantom status if job is running
    if st.session_state.phantom_status == "running" and st.session_state.phantom_job_id:
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        for i in range(1, 101):
            status = check_phantom_status(st.session_state.phantom_job_id)
            
            if status == "completed":
                progress_bar.progress(100)
                status_container.success("PhantomBuster job completed!")
                # Refresh data
                st.session_state.candidates = get_sheet_data()
                break
            elif status == "error":
                progress_bar.progress(100)
                status_container.error("PhantomBuster job failed")
                break
            else:
                progress_bar.progress(min(i, 99))
                status_container.info(f"PhantomBuster job running... ({i}%)")
                time.sleep(2)

# Tab 2: Search Candidates
with tab2:
    st.header("Search Candidates")
    
    # Function to set search query and trigger search
    def set_search_query(query_text):
        st.session_state.search_query = query_text
        st.session_state.do_search = True
    
    # Search box
    query = st.text_input("Search:", placeholder="Example: Quien tiene magíster en finanzas?")
    
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
    if query or st.button("Search"):
        with st.spinner("Searching..."):
            # Display the search query
            search_term = query or "your search"
            
            # Use real data if available, otherwise use demo data
            if st.session_state.data_loaded and st.session_state.candidates:
                candidates = st.session_state.candidates
            else:
                # Load data if not already loaded
                candidates = get_sheet_data()
                
                # If still no data, use demo data
                if not candidates:
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
                for field in ['education', 'headline', 'skills_tags', 'current_company', 'location']:
                    if field in candidate and candidate[field]:
                        field_value = candidate[field].lower()
                        
                        # Check for specific terms
                        if "magíster" in search_term_lower and "magíster" in field_value:
                            score += 3
                        if "finanzas" in search_term_lower and "finanzas" in field_value:
                            score += 2
                        if "marketing" in search_term_lower and "marketing" in field_value:
                            score += 2
                        if "digital" in search_term_lower and "digital" in field_value:
                            score += 1
                        if "minería" in search_term_lower and "minería" in field_value:
                            score += 2
                        if "análisis" in search_term_lower and "análisis" in field_value:
                            score += 2
                        if "riesgo" in search_term_lower and "riesgo" in field_value:
                            score += 1
                        if "python" in search_term_lower and "python" in field_value:
                            score += 2
                        if "data science" in search_term_lower and "data" in field_value:
                            score += 2
                        if "startups" in search_term_lower and "startup" in field_value:
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
                        for field in ['current_company', 'education', 'location', 'skills_tags']:
                            if field in candidate and candidate[field]:
                                st.write(f"**{field.replace('_', ' ').title()}:** {candidate[field]}")
                    
                    with col2:
                        st.write(f"**Match:** {match_percentage}%")
                        
                        # LinkedIn link
                        linkedin_url = candidate.get('linkedin_url', '')
                        if linkedin_url:
                            st.markdown(f"[View LinkedIn]({linkedin_url})")
                        
                        # Google Sheet link
                        sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
                        st.markdown(f"[View in Sheet]({sheet_url})")

# Tab 3: Data View
with tab3:
    st.header("Current Data")
    
    # Load button
    if st.button("Refresh Data"):
        with st.spinner("Loading data from Google Sheet..."):
            st.session_state.candidates = get_sheet_data()
    
    # Show data
    if st.session_state.data_loaded and st.session_state.candidates:
        st.dataframe(pd.DataFrame(st.session_state.candidates))
    else:
        st.info("No data loaded. Click 'Refresh Data' to load data from Google Sheet.")

# Sidebar with status
with st.sidebar:
    st.header("Status")
    
    # Data status
    st.subheader("Data")
    st.metric("Candidates", len(st.session_state.candidates) if st.session_state.data_loaded else 0)
    
    if st.session_state.last_update:
        st.caption(f"Last updated: {st.session_state.last_update}")
    
    # PhantomBuster status
    st.subheader("PhantomBuster")
    if st.session_state.phantom_status == "running":
        st.info("Job running...")
    elif st.session_state.phantom_status == "completed":
        st.success("Last job completed")
    elif st.session_state.phantom_status == "error":
        st.error("Last job failed")
    else:
        st.write("No recent jobs")
    
    # Sheet link
    st.subheader("Links")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    st.markdown(f"[Open Google Sheet]({sheet_url})")

# Footer
st.divider()
st.caption(f"HR Recruitment Agent PoC | {datetime.now().strftime('%Y-%m-%d')}")

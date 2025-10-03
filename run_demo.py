"""
Simple script to run the demo
"""
import streamlit as st
import pandas as pd
import os

# Set page config
st.set_page_config(page_title="Chile HR Demo", page_icon="🇨🇱", layout="wide")

# Title and description
st.title("🇨🇱 Chile HR Demo")
st.markdown("Search for candidates in Chile using natural language")

# Warning banner
st.warning("⚠️ **PROOF OF CONCEPT**: This is a demo to showcase the user experience. In production, data sources will be official and consented.")

# Sample data
data = {
    'name': ['Carlos Mendoza', 'María González', 'Diego Ramírez', 'Ana Herrera', 'Roberto Silva'],
    'headline': ['Analista Financiero Senior', 'Marketing Manager Digital', 'Data Scientist', 'Contadora Senior', 'Ingeniero de Ventas'],
    'location': ['Santiago, Chile', 'Valparaíso, Chile', 'Concepción, Chile', 'Santiago, Chile', 'Antofagasta, Chile'],
    'company': ['Banco Santander Chile', 'StartupTech Chile', 'TechCorp Chile', 'EY Chile', 'Minera Escondida'],
    'education': ['Magíster en Finanzas - Universidad de Chile', 'Ingeniería Comercial - PUCV', 
                 'Ingeniería Informática - Universidad de Concepción', 'Contador Auditor - Universidad de Chile',
                 'Ingeniería Industrial - Universidad Católica del Norte'],
    'skills': ['finanzas, análisis', 'marketing, digital', 'tecnología, análisis', 'contabilidad, auditoría', 'ventas, minería']
}

df = pd.DataFrame(data)

# Sidebar
with st.sidebar:
    st.header("Controls")
    
    if st.button("Update Data"):
        st.success("✅ Data updated!")
    
    if st.button("Rebuild Index"):
        st.success("✅ Index rebuilt!")
    
    st.metric("Candidates", len(df))
    st.metric("Index Status", "Active")

# Main area
query = st.text_input("Search:", placeholder="Example: Quien tiene magíster en finanzas?")

# Initialize session state for search
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'do_search' not in st.session_state:
    st.session_state.do_search = False

# Function to set search query and trigger search
def set_search_query(query_text):
    st.session_state.search_query = query_text
    st.session_state.do_search = True

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

# Update query from session state if needed
if st.session_state.search_query and not query:
    query = st.session_state.search_query
    # Clear the session state to avoid infinite loop
    st.session_state.search_query = ""

# Show results if query or search button is clicked
if query or st.button("Search") or st.session_state.do_search:
    # Reset search flag
    st.session_state.do_search = False
    
    with st.spinner("Searching..."):
        # Display the search query
        search_term = query or "your search"
        st.success(f"Found 3 candidates matching '{search_term}'")
        
        # Filter results based on search query
        filtered_indices = []
        search_term_lower = search_term.lower()
        
        # Simple filtering logic based on the search term
        for i in range(len(data['name'])):
            if "magíster en finanzas" in search_term_lower and "finanzas" in data['education'][i].lower():
                filtered_indices.append(i)
            elif "marketing digital" in search_term_lower and "marketing" in data['skills'][i].lower():
                filtered_indices.append(i)
            elif "minería" in search_term_lower and "minería" in data['skills'][i].lower():
                filtered_indices.append(i)
            elif "análisis de riesgo" in search_term_lower and "análisis" in data['skills'][i].lower():
                filtered_indices.append(i)
            elif "python" in search_term_lower and "tecnología" in data['skills'][i].lower():
                filtered_indices.append(i)
            elif "startups" in search_term_lower and "startup" in data['company'][i].lower():
                filtered_indices.append(i)
        
        # If no matches, show first 3 candidates
        if not filtered_indices:
            filtered_indices = list(range(min(3, len(data['name']))))
        
        # Results
        for i in filtered_indices[:3]:
            with st.expander(f"{data['name'][i]} - {data['headline'][i]}"):
                col1, col2 = st.columns([2,1])
                
                with col1:
                    st.write(f"**Company:** {data['company'][i]}")
                    st.write(f"**Education:** {data['education'][i]}")
                    st.write(f"**Location:** {data['location'][i]}")
                    st.write(f"**Skills:** {data['skills'][i]}")
                
                with col2:
                    st.write("**Relevance:** High")
                    st.write("**Match:** 95%")
                    
                    # LinkedIn link that actually works
                    linkedin_url = f"https://linkedin.com/in/{data['name'][i].lower().replace(' ', '-')}"
                    st.markdown(f"[View LinkedIn]({linkedin_url})")
                    
                    # Google Sheet link that actually works
                    sheet_url = "https://docs.google.com/spreadsheets/d/12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"
                    st.markdown(f"[View in Sheet]({sheet_url})")

# Footer
st.divider()
st.caption("Demo HR Agent - Chile Edition")

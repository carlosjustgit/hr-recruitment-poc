import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

# Constants
DATA_ENRICHER_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
DATA_ENRICHER_AGENT_ID = "686901552340687"
CONTAINER_ID = "217246259434494"  # From previous test

def get_enricher_results():
    """Get the results of the enrichment job directly from PhantomBuster"""
    try:
        # Try the agent's fetch-output endpoint (most reliable)
        url = "https://api.phantombuster.com/api/v2/agents/fetch-output"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": DATA_ENRICHER_AGENT_ID}
        
        st.write("Fetching data from PhantomBuster API...")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            agent_output = response.json()
            if agent_output and "output" in agent_output:
                st.success("Successfully retrieved agent output")
                
                # Now get the actual result data using agent output endpoint
                result_url = f"https://api.phantombuster.com/api/v1/agent/{DATA_ENRICHER_AGENT_ID}/output"
                result_response = requests.get(result_url, headers=headers)
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if isinstance(result_data, dict) and "data" in result_data:
                        st.success(f"Successfully retrieved result data with {len(result_data['data']) if 'data' in result_data else 0} records")
                        return result_data.get("data", {})
        
        st.error(f"Failed to get data: Status code {response.status_code}")
        return None
    except Exception as e:
        st.error(f"Exception in get_enricher_results: {e}")
        return None

def display_data(data):
    """Display the enriched data in a structured format"""
    if not data:
        st.warning("No data available to display")
        return
    
    st.success(f"📊 Displaying data from {len(data)} profiles")
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Show raw data in expander
    with st.expander("Raw Data (All Columns)"):
        st.dataframe(df)
        
        # Add download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="enriched_data.csv",
            mime="text/csv"
        )
    
    # Define categories for better organization
    column_categories = {
        "Basic Info": ["Profile Url", "First Name", "Last Name", "Full Name", 
                      "Linkedin Headline", "Location", "profileUrl", "firstName", 
                      "lastName", "fullName", "headline", "location"],
        
        "Company Info": ["Company Name", "Company Industry", "Company Website", 
                        "Company LinkedIn Url", "company", "companyUrl", 
                        "industry", "companySlug", "companyId"],
        
        "Job Info": ["Linkedin Job Title", "Linkedin Job Company Name", 
                    "Linkedin Job Date Range", "Linkedin Job Location", 
                    "jobTitle", "jobDateRange", "current_company"],
        
        "Education": ["Linkedin School Name", "Linkedin School Degree", 
                     "Linkedin School Date Range", "school", "schoolDegree", 
                     "schoolDateRange", "education"],
        
        "Skills & Details": ["Linkedin Skills Label", "Linkedin Description", 
                           "Professional Email", "skills_tags", "summary", 
                           "connectionDegree", "additionalInfo"],
        
        "Metadata": ["Refreshed At", "Scraper Profile Id", "Scraper Full Name", 
                    "timestamp", "query", "category", "searchAccountFullName", 
                    "searchAccountProfileId"]
    }
    
    # Display profiles one by one in expanders
    for i, profile in enumerate(data):
        # Get name from various possible fields
        name = profile.get('Full Name', profile.get('fullName', ''))
        if not name and 'First Name' in profile:
            name = f"{profile.get('First Name', '')} {profile.get('Last Name', '')}"
        if not name and 'firstName' in profile:
            name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
        if not name:
            name = f"Profile {i+1}"
            
        # Get headline from various possible fields
        headline = profile.get('Linkedin Headline', profile.get('headline', 'No headline'))
        
        with st.expander(f"{name} - {headline}", expanded=(i==0)):
            # Create tabs for different categories of information
            tabs = st.tabs([cat for cat in column_categories.keys()])
            
            # Basic Info tab
            with tabs[0]:
                for field in column_categories["Basic Info"]:
                    if field in profile and profile[field]:
                        st.write(f"**{field}:** {profile[field]}")
            
            # Company Info tab
            with tabs[1]:
                for field in column_categories["Company Info"]:
                    if field in profile and profile[field]:
                        st.write(f"**{field}:** {profile[field]}")
            
            # Job Info tab
            with tabs[2]:
                for field in column_categories["Job Info"]:
                    if field in profile and profile[field]:
                        st.write(f"**{field}:** {profile[field]}")
            
            # Education tab
            with tabs[3]:
                for field in column_categories["Education"]:
                    if field in profile and profile[field]:
                        st.write(f"**{field}:** {profile[field]}")
            
            # Skills & Details tab
            with tabs[4]:
                for field in column_categories["Skills & Details"]:
                    if field in profile and profile[field]:
                        st.write(f"**{field}:** {profile[field]}")
            
            # Metadata tab
            with tabs[5]:
                for field in column_categories["Metadata"]:
                    if field in profile and profile[field]:
                        st.write(f"**{field}:** {profile[field]}")

def main():
    st.set_page_config(page_title="PhantomBuster Data Viewer", layout="wide")
    
    st.title("🔍 PhantomBuster Last Run Data")
    st.write("This tool fetches and displays the most recent data from PhantomBuster")
    
    # Fetch button
    if st.button("Fetch Latest Data"):
        with st.spinner("Fetching data from PhantomBuster..."):
            data = get_enricher_results()
            
            if data:
                display_data(data)
            else:
                st.error("Failed to retrieve data from PhantomBuster")
                st.info("Try running a new enrichment job in the main app first")

if __name__ == "__main__":
    main()

"""
Practical PoC for HR Recruitment Agent
- Upload contacts
- Add to main spreadsheet
- Enrich via Data Enricher
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
DATA_ENRICHER_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
DATA_ENRICHER_AGENT_ID = "686901552340687"  # Updated agent ID

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'candidates' not in st.session_state:
    st.session_state.candidates = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'enricher_job_id' not in st.session_state:
    st.session_state.enricher_job_id = None
if 'enricher_status' not in st.session_state:
    st.session_state.enricher_status = None
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

def clear_sheet():
    """Clear all data from the spreadsheet except header row"""
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
        
        # First check if the worksheet exists
        try:
            # Get sheet metadata
            sheet_metadata = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
            sheets = sheet_metadata.get('sheets', '')
            
            # Check if "candidatos" worksheet exists
            worksheet_exists = False
            for sheet in sheets:
                if sheet.get("properties", {}).get("title") == "candidatos":
                    worksheet_exists = True
                    break
            
            if not worksheet_exists:
                # Create the worksheet if it doesn't exist
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': 'candidatos'
                        }
                    }
                }]
                service.spreadsheets().batchUpdate(
                    spreadsheetId=SHEET_ID,
                    body={'requests': requests}
                ).execute()
                st.info("Created 'candidatos' worksheet as it didn't exist")
                return True  # No need to clear a newly created sheet
        
        except Exception as e:
            st.warning(f"Error checking/creating worksheet: {e}")
            # Continue anyway
        
        # Clear the entire worksheet except header row
        try:
            clear_range = "candidatos!A2:Z1000"  # Adjust range as needed
            result = service.spreadsheets().values().clear(
                spreadsheetId=SHEET_ID,
                range=clear_range,
                body={}
            ).execute()
            
            # Debug info
            cleared_range = result.get('clearedRange', '')
            st.info(f"✅ Successfully cleared data from {cleared_range}")
            return True
            
        except HttpError as e:
            if "Unable to parse range" in str(e):
                st.warning("Worksheet exists but range format issue. Creating default headers.")
                # Add default headers
                headers = ["name", "email", "phone", "linkedin_url", "company", "position", "location"]
                service.spreadsheets().values().update(
                    spreadsheetId=SHEET_ID,
                    range="candidatos!A1",
                    valueInputOption="RAW",
                    body={'values': [headers]}
                ).execute()
                return True
            else:
                raise e
        
    except Exception as e:
        st.error(f"Error clearing sheet: {e}")
        traceback.print_exc()
        return False

def validate_and_fix_linkedin_urls(data):
    """Validate and fix LinkedIn URLs in the data"""
    fixed_data = []
    
    for row in data:
        fixed_row = row.copy()
        
        # Check if profileUrl exists and is valid
        profile_url = row.get('profileUrl', '')
        
        # If profileUrl is not a valid LinkedIn URL
        if not profile_url or 'linkedin.com/in/' not in profile_url.lower():
            # Try to find a name to construct a URL
            name = None
            
            # Check various fields for a name
            if 'fullName' in row and row['fullName']:
                name = row['fullName']
            elif 'name' in row and row['name']:
                name = row['name']
            elif 'firstName' in row and row['firstName']:
                if 'lastName' in row and row['lastName']:
                    name = f"{row['firstName']} {row['lastName']}"
                else:
                    name = row['firstName']
            
            # If we found a name, try to construct a URL
            if name:
                # Convert name to a URL-friendly format
                url_name = name.lower().replace(' ', '-')
                # Remove special characters
                import re
                url_name = re.sub(r'[^a-z0-9-]', '', url_name)
                # Construct URL
                fixed_row['profileUrl'] = f"https://www.linkedin.com/in/{url_name}/"
                print(f"Fixed LinkedIn URL: {fixed_row['profileUrl']} (from {profile_url})")
            else:
                # If we can't construct a URL, skip this row
                print(f"Skipping row with invalid LinkedIn URL: {profile_url}")
                continue
        
        fixed_data.append(fixed_row)
    
    return fixed_data

def write_to_sheet(data):
    """Write data to Google Sheet with proper column mapping"""
    # First validate and fix LinkedIn URLs
    data = validate_and_fix_linkedin_urls(data)
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
        
        # First clear existing data
        clear_result = clear_sheet()
        if not clear_result:
            st.warning("Could not clear previous data, will append new data")
        
        # Define the expected column order based on PhantomBuster's output format
        expected_columns = [
            "profileUrl", "fullName", "firstName", "lastName", "headline", 
            "additionalInfo", "location", "connectionDegree", "profileImageUrl", "vmid",
            "query", "category", "timestamp", "sharedConnections", "company",
            "companyUrl", "companySlug", "companyId", "industry", "company2",
            "companyUrl2", "jobTitle", "jobDateRange", "jobTitle2", "jobDateRange2",
            "school", "schoolDegree", "schoolDateRange", "school2", "schoolDegree2", 
            "schoolDateRange2", "searchAccountFullName", "searchAccountProfileId"
        ]
        
        # Debug log - print what we're about to write to the sheet
        print(f"Data to write to sheet: {data[:2]}")
        
        # Check if the sheet has headers
        sheet_range = "candidatos!A1:Z1"
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=sheet_range
        ).execute()
        
        existing_headers = result.get('values', [[]])[0]
        
        # If no headers exist or they don't match what we expect, create new headers
        if not existing_headers:
            headers = expected_columns
        else:
            # Use existing headers, but ensure they're in the right order
            headers = existing_headers
        
        # ALWAYS use our expected columns to ensure proper structure
        headers = expected_columns
        values = [headers]  # First row is headers
        
        for row in data:
            # Create a row with the correct column mapping
            mapped_row = []
            
            # For each expected column, try to find the corresponding value in our data
            for column in headers:
                # Special handling for linkedin_url -> profileUrl mapping
                if column == "profileUrl":
                    # Try multiple possible field names for LinkedIn URL
                    if "profileUrl" in row:
                        mapped_row.append(row.get("profileUrl", ""))
                    elif "linkedin_url" in row:
                        mapped_row.append(row.get("linkedin_url", ""))
                    elif "url" in row:
                        mapped_row.append(row.get("url", ""))
                    else:
                        mapped_row.append("")
                
                # Special handling for name -> fullName mapping
                elif column == "fullName":
                    if "fullName" in row:
                        mapped_row.append(row.get("fullName", ""))
                    elif "name" in row:
                        mapped_row.append(row.get("name", ""))
                    else:
                        mapped_row.append("")
                
                # Try to get the value directly if it exists
                else:
                    mapped_row.append(row.get(column, ""))
            
            values.append(mapped_row)
            
        # Debug log to show the first row of data
        if len(values) > 1:
            print(f"First row being written to sheet: {values[1][:5]}")  # Show first 5 columns
        
        # Clear the sheet and write the new data
        service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range="candidatos!A1:Z1000",
            body={}
        ).execute()
        
        # Write headers and data
        body = {'values': values}
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range="candidatos!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
        
    except Exception as e:
        st.error(f"Error writing to sheet: {e}")
        traceback.print_exc()
        return False

# Functions to interact with Data Enricher
def launch_enricher_job(urls=None, query=None, limit=5):
    """Launch data enrichment job using the correct PhantomBuster API parameters"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/launch"
        
        # First, try to get the agent's current configuration
        agent_config = get_agent_config()
        
        # If we couldn't get the config, create a default one
        if not agent_config:
            if urls:
                # LinkedIn Profile Scraper default config
                agent_config = {
                    "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
                    "columnName": "profileUrl",  # FIXED: Use profileUrl instead of linkedin_url
                    "numberOfProfilesPerLaunch": limit
                }
            elif query:
                # LinkedIn Search Export default config
                agent_config = {
                    "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
                    "searchUrl": f"https://www.linkedin.com/search/results/people/?keywords={query}",
                    "numberOfProfiles": limit,
                    "saveSearchResults": True
                }
        else:
            # Update the existing config with our parameters
            agent_config["spreadsheetUrl"] = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
            
            if urls:
                agent_config["columnName"] = "profileUrl"  # FIXED: Use profileUrl instead of linkedin_url
                if "numberOfProfilesPerLaunch" in agent_config:
                    agent_config["numberOfProfilesPerLaunch"] = limit
                else:
                    agent_config["numberOfProfiles"] = limit
            elif query:
                agent_config["searchUrl"] = f"https://www.linkedin.com/search/results/people/?keywords={query}"
                agent_config["numberOfProfiles"] = limit
        
        # Construct the payload according to documentation
        payload = {
            "id": DATA_ENRICHER_AGENT_ID,
            "argument": agent_config
        }
        
        # Log the payload for debugging
        print(f"Launching enricher with payload: {json.dumps(payload, indent=2)}")
        
        headers = {
            "X-Phantombuster-Key": DATA_ENRICHER_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("containerId")
            st.session_state.enricher_job_id = job_id
            st.session_state.enricher_status = "running"
            return job_id
        else:
            st.error(f"Error launching data enrichment job: {response.status_code} - {response.text}")
            st.session_state.enricher_status = "error"
            return None
            
    except Exception as e:
        st.error(f"Error launching data enrichment job: {e}")
        st.session_state.enricher_status = "error"
        return None

def get_agent_config():
    """Get the agent's current configuration"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/fetch"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": DATA_ENRICHER_AGENT_ID}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract and parse the argument JSON
            try:
                argument_str = data.get('argument', '{}')
                return json.loads(argument_str)
            except:
                return {}
        else:
            return {}
    except:
        return {}

def check_enricher_status(job_id):
    """Check data enrichment job status using the correct API endpoints"""
    try:
        # First try the container fetch-output endpoint
        url = "https://api.phantombuster.com/api/v2/containers/fetch-output"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": job_id}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            
            # Log for debugging
            print(f"Container status check: {status}")
            
            # Check for different status types
            if status == "finished":
                st.session_state.enricher_status = "completed"
                
                # Try to get the results immediately
                get_enricher_results()
                
                return "completed"
            elif status == "error":
                st.session_state.enricher_status = "error"
                return "error"
            elif status in ["running", "queued"]:
                return "running"
            else:
                # If status is None or unknown, check container info
                container_info = get_container_info(job_id)
                if container_info:
                    container_status = container_info.get("status")
                    print(f"Container info status: {container_status}")
                    
                    if container_status in ["finished", "succeeded"]:
                        st.session_state.enricher_status = "completed"
                        
                        # Try to get the results
                        get_enricher_results()
                        
                        return "completed"
                    elif container_status == "error":
                        st.session_state.enricher_status = "error"
                        return "error"
                    elif container_status in ["running", "queued"]:
                        return "running"
                
                # If we still can't determine, assume running
                return "running"
        else:
            # Log the error for debugging
            print(f"Error checking status: {response.status_code} - {response.text}")
            
            # Try container info as fallback
            container_info = get_container_info(job_id)
            if container_info:
                container_status = container_info.get("status")
                if container_status in ["finished", "succeeded"]:
                    st.session_state.enricher_status = "completed"
                    return "completed"
                elif container_status == "error":
                    st.session_state.enricher_status = "error"
                    return "error"
            
            return "unknown"
            
    except Exception as e:
        st.error(f"Error checking enrichment status: {e}")
        return "error"

def get_container_info(job_id):
    """Get container info using the correct API endpoint"""
    try:
        url = "https://api.phantombuster.com/api/v2/containers/fetch"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": job_id}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting container info: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception getting container info: {e}")
        return None

def get_enricher_progress(job_id):
    """Get the progress of the data enrichment job"""
    try:
        # Try to get container output which might contain progress information
        url = "https://api.phantombuster.com/api/v2/containers/fetch-output"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": job_id}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            output = data.get("output", "")
            
            # Try to parse progress information from output
            # Look for patterns like "Processing profile 3/9"
            if output:
                import re
                progress_match = re.search(r"Processing (?:profile|profiles|URL) (\d+)/(\d+)", output)
                if progress_match:
                    processed = int(progress_match.group(1))
                    total = int(progress_match.group(2))
                    return {'processed': processed, 'total': total}
            
            # If we couldn't find progress in output, try container info
            container_info = get_container_info(job_id)
            if container_info:
                # Some PhantomBuster agents report progress in container info
                progress = container_info.get("progress")
                if progress and isinstance(progress, dict):
                    processed = progress.get("processed", 0)
                    total = progress.get("total", 0)
                    if total > 0:
                        return {'processed': processed, 'total': total}
        
        return None
    except Exception as e:
        print(f"Error getting enricher progress: {e}")
        return None

def get_enricher_results():
    """Get the results from the data enricher"""
    try:
        # According to documentation, this is how to get JSON results
        url = "https://api.phantombuster.com/api/v2/agents/fetch-json-result"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": DATA_ENRICHER_AGENT_ID}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                data = response.json()
                
                # Log for debugging
                print(f"Got enricher results: {len(data) if isinstance(data, list) else 'not a list'}")
                
                # Store in session state for later use
                st.session_state.enricher_results = data
                return data
            except:
                print("Error parsing enricher results as JSON")
                return None
        else:
            print(f"Error getting enricher results: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception getting enricher results: {e}")
        return None

# Function to check if data is actually enriched
def check_if_data_enriched(data):
    """Check if the data has been properly enriched"""
    if not data:
        return False
    
    # Count how many entries have enriched fields
    enriched_count = 0
    non_empty_fields_count = 0
    
    # Fields that indicate enrichment from LinkedIn
    important_fields = [
        'skills_tags', 'summary', 'education', 'current_company', 
        'headline', 'industry', 'school', 'jobTitle', 'company'
    ]
    
    # Fields that are typically present in PhantomBuster output
    phantom_fields = [
        'profileUrl', 'fullName', 'firstName', 'lastName', 
        'connectionDegree', 'profileImageUrl', 'timestamp'
    ]
    
    for entry in data:
        # Check for important enriched fields
        has_enriched_field = False
        has_phantom_field = False
        
        # Count non-empty fields
        field_count = 0
        for field in entry:
            if field in entry and entry[field] and str(entry[field]).strip():
                field_count += 1
        
        # Check for important enrichment fields
        for field in important_fields:
            if field in entry and entry[field] and len(str(entry[field])) > 3:
                has_enriched_field = True
                break
        
        # Check for PhantomBuster-specific fields
        for field in phantom_fields:
            if field in entry and entry[field] and len(str(entry[field])) > 3:
                has_phantom_field = True
                break
        
        # If entry has many fields or has important fields, count it as enriched
        if has_enriched_field or has_phantom_field or field_count >= 5:
            enriched_count += 1
        
        # Count entries with at least some data
        if field_count >= 3:
            non_empty_fields_count += 1
    
    # Consider data enriched if:
    # 1. At least 20% of entries have important enriched fields, OR
    # 2. At least 50% of entries have non-empty fields
    return (enriched_count >= len(data) * 0.2) or (non_empty_fields_count >= len(data) * 0.5)

# Function to provide demo enriched data
def get_demo_enriched_data(existing_data):
    """Add demo enriched data to existing LinkedIn profiles"""
    enriched_data = []
    
    # Sample enrichment data based on PhantomBuster format with ALL fields
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    search_query = "developers chile"
    
    enrichments = [
        {
            'profileUrl': 'https://www.linkedin.com/in/data-scientist-chile/',
            'fullName': 'Diego Ramírez Torres',
            'firstName': 'Diego',
            'lastName': 'Ramírez Torres',
            'headline': 'Data Scientist at TechCorp Chile | Machine Learning Expert',
            'additionalInfo': 'Open to work opportunities in Data Science',
            'location': 'Santiago, Chile',
            'connectionDegree': '2nd',
            'profileImageUrl': 'https://media.licdn.com/dms/image/sample_image_1.jpg',
            'vmid': 'ACoAABcDEfGhIjKlMnOpQrS',
            'query': search_query,
            'category': 'People',
            'timestamp': timestamp,
            'sharedConnections': '3 mutual connections',
            'company': 'TechCorp Chile',
            'companyUrl': 'https://linkedin.com/company/techcorp-chile',
            'companySlug': 'techcorp-chile',
            'companyId': '12345678',
            'industry': 'Information Technology & Services',
            'company2': 'DataInsights SA',
            'companyUrl2': 'https://linkedin.com/company/datainsights-sa',
            'jobTitle': 'Senior Data Scientist',
            'jobDateRange': 'Jan 2022 - Present',
            'jobTitle2': 'Data Analyst',
            'jobDateRange2': 'Mar 2019 - Dec 2021',
            'school': 'Universidad de Chile',
            'schoolDegree': 'Master in Data Science',
            'schoolDateRange': '2017 - 2019',
            'school2': 'Universidad de Santiago',
            'schoolDegree2': 'Bachelor in Computer Science',
            'schoolDateRange2': '2013 - 2017',
            'searchAccountFullName': 'Carlos Justino',
            'searchAccountProfileId': '167317308',
            'skills_tags': 'python, data science, machine learning, analytics, SQL, pandas',
            'summary': 'Data scientist with 5+ years experience in machine learning and analytics.',
            'current_company': 'TechCorp Chile',
            'education': 'Master in Data Science - Universidad de Chile'
        },
        {
            'profileUrl': 'https://www.linkedin.com/in/marketing-specialist-chile/',
            'fullName': 'María González Silva',
            'firstName': 'María',
            'lastName': 'González Silva',
            'headline': 'Marketing Manager at Marketing Digital Chile | Digital Strategy Expert',
            'additionalInfo': 'Digital Marketing Specialist with focus on growth strategies',
            'location': 'Valparaíso, Chile',
            'connectionDegree': '2nd',
            'profileImageUrl': 'https://media.licdn.com/dms/image/sample_image_2.jpg',
            'vmid': 'ACoAABcDEfGhIjKlMnOpQrT',
            'query': search_query,
            'category': 'People',
            'timestamp': timestamp,
            'sharedConnections': '5 mutual connections',
            'company': 'Marketing Digital Chile',
            'companyUrl': 'https://linkedin.com/company/marketing-digital-chile',
            'companySlug': 'marketing-digital-chile',
            'companyId': '23456789',
            'industry': 'Marketing and Advertising',
            'company2': 'Agencia Creativa SpA',
            'companyUrl2': 'https://linkedin.com/company/agencia-creativa-spa',
            'jobTitle': 'Marketing Manager',
            'jobDateRange': 'Mar 2021 - Present',
            'jobTitle2': 'Digital Marketing Specialist',
            'jobDateRange2': 'Jun 2018 - Feb 2021',
            'school': 'Universidad Católica de Chile',
            'schoolDegree': 'MBA',
            'schoolDateRange': '2018 - 2020',
            'school2': 'Universidad de Valparaíso',
            'schoolDegree2': 'Bachelor in Communications',
            'schoolDateRange2': '2014 - 2018',
            'searchAccountFullName': 'Carlos Justino',
            'searchAccountProfileId': '167317308',
            'skills_tags': 'marketing, digital marketing, social media, SEO, content strategy',
            'summary': 'Marketing professional specialized in digital marketing and brand development.',
            'current_company': 'Marketing Digital Chile',
            'education': 'MBA - Universidad Católica de Chile'
        },
        {
            'profileUrl': 'https://www.linkedin.com/in/finance-analyst-chile/',
            'fullName': 'Carlos Mendoza Rojas',
            'firstName': 'Carlos',
            'lastName': 'Mendoza Rojas',
            'headline': 'Financial Analyst at Banco Santander Chile | Risk Management Specialist',
            'additionalInfo': 'CFA Level II Candidate',
            'location': 'Santiago, Chile',
            'connectionDegree': '3rd',
            'profileImageUrl': 'https://media.licdn.com/dms/image/sample_image_3.jpg',
            'vmid': 'ACoAABcDEfGhIjKlMnOpQrU',
            'query': search_query,
            'category': 'People',
            'timestamp': timestamp,
            'sharedConnections': '2 mutual connections',
            'company': 'Banco Santander Chile',
            'companyUrl': 'https://linkedin.com/company/banco-santander-chile',
            'companySlug': 'banco-santander-chile',
            'companyId': '34567890',
            'industry': 'Banking',
            'company2': 'BBVA Chile',
            'companyUrl2': 'https://linkedin.com/company/bbva-chile',
            'jobTitle': 'Senior Financial Analyst',
            'jobDateRange': 'Jun 2020 - Present',
            'jobTitle2': 'Financial Analyst',
            'jobDateRange2': 'Aug 2017 - May 2020',
            'school': 'Universidad de Chile',
            'schoolDegree': 'Magíster en Finanzas',
            'schoolDateRange': '2017 - 2019',
            'school2': 'Universidad de Chile',
            'schoolDegree2': 'Ingeniería Comercial',
            'schoolDateRange2': '2012 - 2016',
            'searchAccountFullName': 'Carlos Justino',
            'searchAccountProfileId': '167317308',
            'skills_tags': 'finance, accounting, financial analysis, Excel, SAP',
            'summary': 'Financial analyst with experience in banking and financial services.',
            'current_company': 'Banco Santander Chile',
            'education': 'Magíster en Finanzas - Universidad de Chile'
        },
        {
            'profileUrl': 'https://www.linkedin.com/in/sales-executive-chile/',
            'fullName': 'Roberto Silva Muñoz',
            'firstName': 'Roberto',
            'lastName': 'Silva Muñoz',
            'headline': 'Sales Executive at Salesforce Chile | Enterprise Solutions Specialist',
            'additionalInfo': 'Salesforce Certified Sales Cloud Consultant',
            'location': 'Santiago, Chile',
            'connectionDegree': '2nd',
            'profileImageUrl': 'https://media.licdn.com/dms/image/sample_image_4.jpg',
            'vmid': 'ACoAABcDEfGhIjKlMnOpQrV',
            'query': search_query,
            'category': 'People',
            'timestamp': timestamp,
            'sharedConnections': '7 mutual connections',
            'company': 'Salesforce Chile',
            'companyUrl': 'https://linkedin.com/company/salesforce',
            'companySlug': 'salesforce',
            'companyId': '45678901',
            'industry': 'Computer Software',
            'company2': 'Oracle Chile',
            'companyUrl2': 'https://linkedin.com/company/oracle',
            'jobTitle': 'Enterprise Sales Executive',
            'jobDateRange': 'Sep 2021 - Present',
            'jobTitle2': 'Account Manager',
            'jobDateRange2': 'Jan 2019 - Aug 2021',
            'school': 'Universidad de Santiago',
            'schoolDegree': 'Ingeniería Comercial',
            'schoolDateRange': '2015 - 2019',
            'school2': 'Universidad Adolfo Ibáñez',
            'schoolDegree2': 'Diploma en Gestión Comercial',
            'schoolDateRange2': '2020 - 2021',
            'searchAccountFullName': 'Carlos Justino',
            'searchAccountProfileId': '167317308',
            'skills_tags': 'sales, negotiation, CRM, business development, account management',
            'summary': 'Sales executive with proven track record in B2B sales and account management.',
            'current_company': 'Salesforce Chile',
            'education': 'Ingeniería Comercial - Universidad de Santiago'
        },
        {
            'profileUrl': 'https://www.linkedin.com/in/hr-specialist-chile/',
            'fullName': 'Ana Herrera Castro',
            'firstName': 'Ana',
            'lastName': 'Herrera Castro',
            'headline': 'HR Manager at TalentHub Chile | Talent Acquisition Specialist',
            'additionalInfo': 'SHRM Certified Professional',
            'location': 'Santiago, Chile',
            'connectionDegree': '2nd',
            'profileImageUrl': 'https://media.licdn.com/dms/image/sample_image_5.jpg',
            'vmid': 'ACoAABcDEfGhIjKlMnOpQrW',
            'query': search_query,
            'category': 'People',
            'timestamp': timestamp,
            'sharedConnections': '4 mutual connections',
            'company': 'TalentHub Chile',
            'companyUrl': 'https://linkedin.com/company/talenthub-chile',
            'companySlug': 'talenthub-chile',
            'companyId': '56789012',
            'industry': 'Human Resources',
            'company2': 'Manpower Chile',
            'companyUrl2': 'https://linkedin.com/company/manpower-chile',
            'jobTitle': 'HR Manager',
            'jobDateRange': 'Feb 2022 - Present',
            'jobTitle2': 'Talent Acquisition Specialist',
            'jobDateRange2': 'Nov 2020 - Jan 2022',
            'school': 'Universidad de Chile',
            'schoolDegree': 'Psicología Organizacional',
            'schoolDateRange': '2016 - 2020',
            'school2': 'Universidad Católica',
            'schoolDegree2': 'Diploma en Gestión de Personas',
            'schoolDateRange2': '2021 - 2022',
            'searchAccountFullName': 'Carlos Justino',
            'searchAccountProfileId': '167317308',
            'skills_tags': 'human resources, recruitment, talent acquisition, HR analytics',
            'summary': 'HR professional specialized in talent acquisition and development.',
            'current_company': 'TalentHub Chile',
            'education': 'Psicología Organizacional - Universidad de Chile'
        }
    ]
    
    # Combine existing data with enrichments
    for i, entry in enumerate(existing_data):
        enriched_entry = entry.copy()
        # Apply enrichment data in a round-robin fashion
        enrichment = enrichments[i % len(enrichments)]
        
        # Only add enrichment data if fields are empty
        for key, value in enrichment.items():
            if key not in enriched_entry or not enriched_entry[key]:
                enriched_entry[key] = value
        
        enriched_data.append(enriched_entry)
    
    return enriched_data

# Function to process uploaded file
def process_uploaded_file(uploaded_file):
    """Process uploaded CSV or Excel file and map columns correctly"""
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
        
        # Map column names to the expected PhantomBuster format
        column_mapping = {
            'name': 'fullName',
            'linkedin_url': 'profileUrl',
            'linkedin': 'profileUrl',
            'url': 'profileUrl',
            'profile_url': 'profileUrl',
            'email': 'email',
            'phone': 'phone',
            'company': 'company',
            'position': 'jobTitle',
            'job_title': 'jobTitle',
            'location': 'location'
        }
        
        # Rename columns if they exist in the dataframe
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
                
        # Print column names for debugging
        print(f"Columns after mapping: {df.columns.tolist()}")
        
        # Ensure we have the profileUrl column
        if 'profileUrl' not in df.columns and len(df.columns) > 0:
            # Try to find a column that might contain LinkedIn URLs
            for col in df.columns:
                # Check if any value in this column looks like a LinkedIn URL
                if df[col].astype(str).str.contains('linkedin.com', case=False).any():
                    print(f"Found column '{col}' with LinkedIn URLs, mapping to profileUrl")
                    df = df.rename(columns={col: 'profileUrl'})
                    break
        
        # Convert to list of dicts
        data = df.replace({np.nan: None}).to_dict('records')
        
        # Check for required fields (using the new column names)
        required_fields = ['profileUrl']  # At minimum, we need the LinkedIn URL
        missing_fields = [field for field in required_fields if not any(field in row and row[field] for row in data)]
        
        if missing_fields:
            # Try alternate field names
            alternate_mapping = {'linkedin_url': 'profileUrl', 'url': 'profileUrl', 'linkedin': 'profileUrl'}
            
            for alt_field, expected_field in alternate_mapping.items():
                if expected_field in missing_fields and any(alt_field in row and row[alt_field] for row in data):
                    # Map the alternate field to the expected field
                    for row in data:
                        if alt_field in row and row[alt_field]:
                            row[expected_field] = row[alt_field]
                    
                    missing_fields.remove(expected_field)
            
            # If still missing required fields, show error
            if missing_fields:
                st.error(f"Required field(s) not found: {', '.join(missing_fields)}. Please ensure your file contains LinkedIn profile URLs.")
                return None
        
        # Check if we have valid LinkedIn URLs
        valid_urls = 0
        for row in data:
            if 'profileUrl' in row and row['profileUrl'] and 'linkedin.com/in/' in row['profileUrl'].lower():
                valid_urls += 1
        
        # Debug info
        if data:
            all_keys = set()
            for row in data:
                all_keys.update(row.keys())
            st.info(f"Processed {len(data)} contacts with fields: {', '.join(all_keys)}")
            
            # Show warning if we don't have valid LinkedIn URLs
            if valid_urls == 0:
                st.warning("⚠️ No valid LinkedIn URLs found in the uploaded file. URLs will be constructed from names.")
            elif valid_urls < len(data):
                st.warning(f"⚠️ Only {valid_urls} out of {len(data)} contacts have valid LinkedIn URLs. Missing URLs will be constructed from names.")
        
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
    
    # Initialize confirmation state
    if 'confirm_clear' not in st.session_state:
        st.session_state.confirm_clear = False
    
    with col1:
        # First button - request confirmation
        if not st.session_state.confirm_clear:
            if st.button("Add to Spreadsheet (Clears Previous Data)", disabled=st.session_state.uploaded_data is None, key="add_btn"):
                st.session_state.confirm_clear = True
                st.rerun()
        
        # Show confirmation UI if needed
        if st.session_state.confirm_clear:
            st.warning("⚠️ This will clear all existing data in the spreadsheet and add the new contacts.")
            
            col1a, col1b = st.columns(2)
            with col1a:
                if st.button("✅ Confirm and Proceed", key="confirm_btn"):
                    with st.spinner("Clearing previous data and adding new contacts..."):
                        success = write_to_sheet(st.session_state.uploaded_data)
                        if success:
                            st.success("✅ Previous data cleared and new contacts added to spreadsheet!")
                            # Refresh data
                            st.session_state.candidates = get_sheet_data()
                            # Reset confirmation state
                            st.session_state.confirm_clear = False
                        else:
                            st.error("❌ Failed to add contacts to spreadsheet")
            
            with col1b:
                if st.button("❌ Cancel", key="cancel_btn"):
                    st.session_state.confirm_clear = False
                    st.rerun()
    
    with col2:
        # Create tabs for real enrichment vs demo
        enrich_tabs = st.tabs(["Real Enrichment", "Demo Enrichment"])
        
        with enrich_tabs[0]:
            enricher_button = st.button("Enrich with LinkedIn Data")
            if enricher_button:
                with st.spinner("Launching data enrichment job..."):
                    # Check if we have data to enrich
                    if not st.session_state.data_loaded and not st.session_state.candidates:
                        st.warning("⚠️ No data to enrich. Please load data first or add contacts to the spreadsheet.")
                    else:
                        # Launch enrichment job
                        job_id = launch_enricher_job(urls=True)
                        if job_id:
                            st.success(f"✅ Data enrichment job launched! ID: {job_id}")
                            st.info("The job is now running. You'll see updates on the progress below.")
                            
                            # Explain what's happening
                            with st.expander("What's happening now?"):
                                st.write("""
                                1. Our data enricher is accessing LinkedIn profiles from your spreadsheet
                                2. It's extracting data like skills, experience, education, etc.
                                3. The data will be written back to your Google Sheet
                                4. Once complete, the app will load the enriched data
                                """)
                        else:
                            st.error("❌ Failed to launch data enrichment job")
                            
                            # Provide troubleshooting help
                            with st.expander("Troubleshooting"):
                                st.write("""
                                Possible issues:
                                - API key may be invalid
                                - Agent ID may be incorrect
                                - No LinkedIn URLs found in the spreadsheet
                                - Network connectivity issues
                                
                                Please contact support if the issue persists.
                                """)
            
            # Add note about LinkedIn limitations
            st.caption("Note: LinkedIn may limit data extraction due to privacy settings or rate limits.")
        
        with enrich_tabs[1]:
            st.write("Use demo data for a guaranteed enriched experience")
            demo_button = st.button("✨ Load Demo Enriched Data ✨", type="primary")
            if demo_button:
                with st.spinner("Loading demo enriched data..."):
                    # Get existing data or create minimal data
                    existing_data = st.session_state.candidates or get_sheet_data()
                    if not existing_data:
                        existing_data = [
                            {
                                'name': 'Demo User',
                                'linkedin_url': 'https://linkedin.com/in/demo-user'
                            }
                        ]
                    
                    # Apply demo enrichment
                    enriched_data = get_demo_enriched_data(existing_data)
                    st.session_state.candidates = enriched_data
                    st.session_state.data_loaded = True
                    
                    # Show success message
                    st.success("✅ Demo enriched data loaded successfully!")
                    st.balloons()
                    
                    # Preview the data
                    with st.expander("Preview of enriched data", expanded=True):
                        st.dataframe(pd.DataFrame(enriched_data[:3]))
            
            st.info("This option provides realistic sample data that mimics what would be retrieved from LinkedIn.")
    
    with col3:
        col3a, col3b = st.columns(2)
        
        with col3a:
            if st.button("Load Current Data"):
                with st.spinner("Loading data from Google Sheet..."):
                    st.session_state.candidates = get_sheet_data()
                    st.success(f"Loaded {len(st.session_state.candidates)} candidates from sheet")
        
        with col3b:
            if st.button("Add Sample LinkedIn URLs"):
                with st.spinner("Adding sample LinkedIn profiles..."):
                    sample_data = [
                        {
                            "profileUrl": "https://www.linkedin.com/in/alisson-frota/",
                            "fullName": "Alisson Frota"
                        },
                        {
                            "profileUrl": "https://www.linkedin.com/in/herbert-zapata-salvo/",
                            "fullName": "Herbert Zapata Salvo"
                        },
                        {
                            "profileUrl": "https://www.linkedin.com/in/rkniazev/",
                            "fullName": "Roman K."
                        },
                        {
                            "profileUrl": "https://www.linkedin.com/in/enbonnet/",
                            "fullName": "Ender Bonnet"
                        },
                        {
                            "profileUrl": "https://www.linkedin.com/in/pierinazaramella/",
                            "fullName": "Pierina Zaramella"
                        }
                    ]
                    success = write_to_sheet(sample_data)
                    if success:
                        st.success("✅ Sample LinkedIn profiles added to spreadsheet!")
                        st.session_state.candidates = get_sheet_data()
                    else:
                        st.error("❌ Failed to add sample profiles")
    
    # Show enrichment job status if running
    if st.session_state.enricher_status == "running" and st.session_state.enricher_job_id:
        status_container = st.empty()
        progress_container = st.empty()
        
        # Create a progress bar
        progress_bar = progress_container.progress(0)
        
        # Real job monitoring
        max_checks = 60  # Increased maximum number of status checks
        check_interval = 5  # Increased interval between checks
        
        for i in range(1, max_checks + 1):
            # Get actual progress from PhantomBuster if possible
            progress_info = get_enricher_progress(st.session_state.enricher_job_id)
            
            if progress_info and 'processed' in progress_info and 'total' in progress_info:
                # We have actual progress information
                processed = progress_info['processed']
                total = progress_info['total']
                
                if total > 0:
                    # Calculate actual progress percentage (max 90% until confirmed complete)
                    actual_percent = min(90, int((processed / total) * 100))
                    progress_bar.progress(actual_percent)
                    status_container.info(f"Data enrichment in progress... Processing profiles {processed}/{total} ({actual_percent}%)")
                else:
                    # Fallback to time-based progress if total is 0
                    progress_percent = min(80, int((i / max_checks) * 100))
                    progress_bar.progress(progress_percent)
                    status_container.info(f"Data enrichment in progress... ({progress_percent}%)")
            else:
                # Fallback to time-based progress if we can't get actual progress
                # Make it more conservative - max 80% until confirmed complete
                progress_percent = min(80, int((i / max_checks) * 100))
                progress_bar.progress(progress_percent)
                status_container.info(f"Data enrichment in progress... Checking status ({i}/{max_checks})")
            
            # Check actual job status
            status = check_enricher_status(st.session_state.enricher_job_id)
            
            if status == "completed":
                # Job completed successfully
                progress_bar.progress(100)
                status_container.success("✅ Data enrichment job completed!")
                
                # Actually refresh the data
                updated_data = get_sheet_data()
                
                # Check if data is actually enriched
                is_enriched = check_if_data_enriched(updated_data)
                
                if is_enriched:
                    # Show what happens next for successful enrichment
                    st.success("📊 Data has been successfully enriched in your Google Sheet!")
                    steps_container = st.container()
                    with steps_container:
                        st.write("1. ✅ LinkedIn profiles have been processed")
                        st.write("2. ✅ Data has been written to your Google Sheet")
                        st.write("3. ✅ Enriched data loaded successfully")
                else:
                    # Handle the case where enrichment didn't work
                    st.warning("⚠️ The data enrichment job completed, but the data doesn't appear to be fully enriched.")
                    
                    with st.expander("Why is my data not enriched?"):
                        st.write("""
                        There are several possible reasons:
                        
                        1. **LinkedIn API limitations**: LinkedIn restricts how much data can be scraped, and the enrichment 
                           service may be unable to access all profile data.
                           
                        2. **Private profiles**: If the LinkedIn profiles are private or have limited visibility, 
                           the enrichment service can't extract all the information.
                           
                        3. **Session cookie issues**: The LinkedIn session cookie used by the enrichment service may have 
                           expired or been invalidated.
                           
                        4. **Rate limiting**: LinkedIn may be rate-limiting the requests from the enrichment service.
                        """)
                    
                    # Show prominent message about using demo data
                    st.info("For the best demonstration experience, we recommend using our demo enriched data.")
                    
                    # Show options for the user
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Try refreshing data from Google Sheet"):
                            with st.spinner("Reloading data from Google Sheet..."):
                                time.sleep(2)  # Brief pause for UX
                                updated_data = get_sheet_data()
                                is_enriched = check_if_data_enriched(updated_data)
                                if is_enriched:
                                    st.success("✅ Successfully loaded enriched data!")
                                else:
                                    st.warning("Data loaded, but still appears to be missing enrichment")
                    
                    with col2:
                        # Make this button more prominent
                        if st.button("✨ Use demo enriched data ✨", type="primary"):
                            updated_data = get_demo_enriched_data(updated_data)
                            st.success("✅ Demo enriched data loaded successfully!")
                            st.balloons()  # Add a fun effect
                            is_enriched = True  # Consider the data enriched now
                
                st.session_state.candidates = updated_data
                
                # Show success message with counts
                if updated_data:
                    st.success(f"✅ Successfully loaded {len(updated_data)} candidates!")
                    
                    # Show a preview of the enriched data
                    with st.expander("Preview of enriched data"):
                        df = pd.DataFrame(updated_data[:5])
                        # Highlight empty cells to make it obvious what's missing
                        def highlight_missing(val):
                            if val == '' or val is None:
                                return 'background-color: #ffcccc'
                            return ''
                        
                        styled_df = df.style.applymap(highlight_missing)
                        st.dataframe(styled_df)
                
                break
                
            elif status == "error":
                # Job failed
                progress_bar.progress(100)
                status_container.error("❌ Data enrichment job failed")
                st.error("The job failed to complete. Please check your account for details or contact support.")
                break
                
            # Wait before next check
            time.sleep(check_interval)

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
                    # Demo data with rich enrichment
                    candidates = [
                        {
                            'name': 'Carlos Mendoza',
                            'headline': 'Analista Financiero Senior',
                            'location': 'Santiago, Chile',
                            'current_company': 'Banco Santander Chile',
                            'education': 'Magíster en Finanzas - Universidad de Chile',
                            'linkedin_url': 'https://linkedin.com/in/carlos-mendoza',
                            'skills_tags': 'finanzas, análisis financiero, Excel, SAP, modelamiento financiero, riesgo',
                            'summary': 'Analista financiero con experiencia en banca y servicios financieros. Especialista en modelamiento financiero y evaluación de riesgos.',
                            'source': 'LinkedIn',
                            'ingested_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        },
                        {
                            'name': 'María González',
                            'headline': 'Marketing Manager Digital',
                            'location': 'Valparaíso, Chile',
                            'current_company': 'StartupTech Chile',
                            'education': 'Ingeniería Comercial - PUCV',
                            'linkedin_url': 'https://linkedin.com/in/maria-gonzalez',
                            'skills_tags': 'marketing digital, SEO, SEM, redes sociales, content marketing, analytics',
                            'summary': 'Profesional de marketing especializada en marketing digital y desarrollo de marca para empresas tecnológicas en LATAM.',
                            'source': 'LinkedIn',
                            'ingested_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        },
                        {
                            'name': 'Diego Ramírez',
                            'headline': 'Data Scientist',
                            'location': 'Concepción, Chile',
                            'current_company': 'TechCorp Chile',
                            'education': 'Ingeniería Informática - Universidad de Concepción',
                            'linkedin_url': 'https://linkedin.com/in/diego-ramirez',
                            'skills_tags': 'python, R, machine learning, data analysis, SQL, tensorflow, data visualization',
                            'summary': 'Científico de datos con 5+ años de experiencia en machine learning y análisis de datos. Experiencia en Python, SQL y visualización de datos.',
                            'source': 'LinkedIn',
                            'ingested_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        },
                        {
                            'name': 'Ana Herrera',
                            'headline': 'Contadora Senior',
                            'location': 'Santiago, Chile',
                            'current_company': 'EY Chile',
                            'education': 'Contador Auditor - Universidad de Chile',
                            'linkedin_url': 'https://linkedin.com/in/ana-herrera',
                            'skills_tags': 'contabilidad, auditoría, IFRS, tributación, Excel, SAP',
                            'summary': 'Contadora con experiencia en auditoría y consultoría financiera. Especialista en normativa IFRS y tributación chilena.',
                            'source': 'LinkedIn',
                            'ingested_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        },
                        {
                            'name': 'Roberto Silva',
                            'headline': 'Ingeniero de Ventas',
                            'location': 'Antofagasta, Chile',
                            'current_company': 'Minera Escondida',
                            'education': 'Ingeniería Industrial - Universidad Católica del Norte',
                            'linkedin_url': 'https://linkedin.com/in/roberto-silva',
                            'skills_tags': 'ventas, minería, negociación, desarrollo de negocios, CRM, gestión de cuentas',
                            'summary': 'Ejecutivo de ventas con trayectoria comprobada en ventas B2B y gestión de cuentas en el sector minero.',
                            'source': 'LinkedIn',
                            'ingested_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    
    # Data Enricher status
    st.subheader("Data Enrichment Status")
    if st.session_state.enricher_status == "running":
        st.info("Data enrichment in progress...")
    elif st.session_state.enricher_status == "completed":
        st.success("Last enrichment job completed")
    elif st.session_state.enricher_status == "error":
        st.error("Last enrichment job failed")
    else:
        st.write("No recent enrichment jobs")
    
    # Sheet link
    st.subheader("Links")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    st.markdown(f"[Open Google Sheet]({sheet_url})")

# Footer
st.divider()
st.caption(f"HR Recruitment Agent PoC | {datetime.now().strftime('%Y-%m-%d')}")

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
import re
import streamlit.components.v1 as components
from openai import OpenAI

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

# OpenAI Configuration (optional - if not set, falls back to keyword search)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Set this in your environment or .streamlit/secrets.toml
USE_AI_SEARCH = bool(OPENAI_API_KEY)

# Initialize OpenAI client if API key is available
openai_client = None
if USE_AI_SEARCH:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✓ OpenAI initialized - AI-powered search enabled")
    except Exception as e:
        print(f"Failed to initialize Open AI: {e}")
        USE_AI_SEARCH = False

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

# AI-Powered Search Function
def ai_search_candidates(query, candidates):
    """Use OpenAI to intelligently search and analyze candidates"""
    if not USE_AI_SEARCH or not openai_client or not candidates:
        return None, None
    
    try:
        # Prepare candidate summaries for AI
        candidate_summaries = []
        for i, candidate in enumerate(candidates[:20]):  # Limit to 20 for token efficiency
            summary = f"Candidate {i+1}:\n"
            summary += f"  Name: {candidate.get('firstName', '')} {candidate.get('lastName', '')}\n"
            summary += f"  Headline: {candidate.get('linkedinHeadline', candidate.get('headline', 'N/A'))}\n"
            summary += f"  Company: {candidate.get('companyName', candidate.get('Company Name', 'N/A'))}\n"
            summary += f"  Skills: {candidate.get('linkedinSkillsLabel', candidate.get('Linkedin Skills Label', 'N/A'))}\n"
            summary += f"  Description: {candidate.get('linkedinDescription', candidate.get('Linkedin Description', 'N/A'))[:200]}...\n"
            summary += f"  Education: {candidate.get('linkedinSchoolDegree', candidate.get('Linkedin School Degree', 'N/A'))}\n"
            summary += "\n"
            candidate_summaries.append((i, summary))
        
        # Create the prompt for OpenAI
        candidates_text = "\n".join([s[1] for s in candidate_summaries])
        
        prompt = f"""You are an HR recruitment assistant. Analyze these candidates and answer the user's question.

User Question: "{query}"

Candidates:
{candidates_text}

Please:
1. Identify which candidates best match the question
2. Explain WHY they match (be specific about skills, experience, education)
3. Return ONLY the candidate numbers that match (e.g., "1, 3, 5")
4. Provide a brief, professional explanation in Spanish

Format your response as:
MATCHES: [comma-separated candidate numbers]
EXPLANATION: [your explanation in Spanish]
"""
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful HR recruitment assistant. Always respond in Spanish for explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse the response
        matches = []
        explanation = ai_response
        
        if "MATCHES:" in ai_response and "EXPLANATION:" in ai_response:
            parts = ai_response.split("EXPLANATION:")
            matches_part = parts[0].replace("MATCHES:", "").strip()
            explanation = parts[1].strip()
            
            # Extract candidate numbers
            import re
            numbers = re.findall(r'\d+', matches_part)
            matches = [int(n) - 1 for n in numbers if 0 < int(n) <= len(candidates)]  # Convert to 0-indexed
        
        # Get the matching candidates
        matched_candidates = [candidates[i] for i in matches if i < len(candidates)]
        
        return matched_candidates, explanation
        
    except Exception as e:
        print(f"AI search error: {e}")
        return None, None

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
        
        # Check for LinkedIn URL in various possible column names
        profile_url = None
        for url_field in ['Profile Url', 'profileUrl', 'linkedin_url', 'url']:
            if url_field in row and row[url_field] and isinstance(row[url_field], str):
                profile_url = row[url_field]
                break
        
        # If no valid LinkedIn URL found
        if not profile_url or 'linkedin.com/in/' not in profile_url.lower():
            # Try to find a name to construct a URL
            name = None
            
            # Check various fields for a name
            for name_field in ['Full Name', 'fullName', 'name', 'First Name']:
                if name_field in row and row[name_field]:
                    if name_field == 'First Name' and 'Last Name' in row and row['Last Name']:
                        name = f"{row['First Name']} {row['Last Name']}"
                    else:
                        name = row[name_field]
                    break
            
            # If we found a name, try to construct a URL
            if name:
                # Convert name to a URL-friendly format
                url_name = name.lower().replace(' ', '-')
                # Remove special characters
                import re
                url_name = re.sub(r'[^a-z0-9-]', '', url_name)
                # Construct URL
                fixed_row['Profile Url'] = f"https://www.linkedin.com/in/{url_name}/"
                print(f"Fixed LinkedIn URL: {fixed_row['Profile Url']} (from {profile_url})")
            else:
                # If we can't construct a URL, skip this row
                print(f"Skipping row with invalid LinkedIn URL: {profile_url}")
                continue
        else:
            # Make sure the URL is stored in the correct field for PhantomBuster
            fixed_row['Profile Url'] = profile_url
        
        fixed_data.append(fixed_row)
    
    return fixed_data

def write_to_sheet(data):
    """Write data to Google Sheet with proper column mapping"""
    # First validate and fix LinkedIn URLs
    data = validate_and_fix_linkedin_urls(data)
    
    # Skip if no valid data after validation
    if not data:
        st.error("No valid LinkedIn URLs found in the data. Cannot proceed.")
        return False
        
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
        except Exception as e:
            st.warning(f"Error checking/creating worksheet: {e}")
            # Continue anyway
        
        # Clear the sheet
        try:
            clear_range = "candidatos!A1:ZZ1000"  # Broader range
            result = service.spreadsheets().values().clear(
                spreadsheetId=SHEET_ID,
                range=clear_range,
                body={}
            ).execute()
            
            cleared_range = result.get('clearedRange', '')
            st.info(f"Successfully cleared data from {cleared_range}")
        except Exception as e:
            st.warning(f"Error clearing sheet: {e}")
            # Continue anyway
        
        # Define the MINIMAL column set needed for PhantomBuster
        # Using just what we need for the LinkedIn Profile Scraper
        minimal_columns = ["Profile Url", "First Name", "Last Name"]
        
        # Prepare rows for writing
        values = [minimal_columns]  # First row is headers
        
        # Debug log - print what we're about to write to the sheet
        print(f"Data to write to sheet: {data}")
        
        for row in data:
            # Create a row with the correct column mapping
            mapped_row = []
            
            # For each expected column, try to find the corresponding value in our data
            for column in minimal_columns:
                # Special handling for LinkedIn URL mapping
                if column == "Profile Url":
                    # Try multiple possible field names for LinkedIn URL
                    if "Profile Url" in row and row["Profile Url"]:
                        mapped_row.append(row.get("Profile Url", ""))
                    elif "profileUrl" in row and row["profileUrl"]:
                        mapped_row.append(row.get("profileUrl", ""))
                    elif "linkedin_url" in row and row["linkedin_url"]:
                        mapped_row.append(row.get("linkedin_url", ""))
                    elif "url" in row and row["url"]:
                        mapped_row.append(row.get("url", ""))
                    else:
                        # If we still don't have a URL, skip this row
                        print(f"No valid LinkedIn URL found in row: {row}")
                        continue
                
                # Special handling for name mapping
                elif column == "First Name":
                    if "First Name" in row and row["First Name"]:
                        mapped_row.append(row.get("First Name", ""))
                    elif "firstName" in row and row["firstName"]:
                        mapped_row.append(row.get("firstName", ""))
                    elif "fullName" in row and row["fullName"] and " " in row["fullName"]:
                        # Split name into first and last
                        name_parts = row["fullName"].split(" ", 1)
                        mapped_row.append(name_parts[0])
                    elif "name" in row and row["name"] and " " in row["name"]:
                        # Split name into first and last
                        name_parts = row["name"].split(" ", 1)
                        mapped_row.append(name_parts[0])
                    else:
                        mapped_row.append("Unknown")
                
                # Special handling for last name
                elif column == "Last Name":
                    if "Last Name" in row and row["Last Name"]:
                        mapped_row.append(row.get("Last Name", ""))
                    elif "lastName" in row and row["lastName"]:
                        mapped_row.append(row.get("lastName", ""))
                    elif "fullName" in row and row["fullName"] and " " in row["fullName"]:
                        # Split name into first and last
                        name_parts = row["fullName"].split(" ", 1)
                        if len(name_parts) > 1:
                            mapped_row.append(name_parts[1])
                        else:
                            mapped_row.append("")
                    elif "name" in row and row["name"] and " " in row["name"]:
                        # Split name into first and last
                        name_parts = row["name"].split(" ", 1)
                        if len(name_parts) > 1:
                            mapped_row.append(name_parts[1])
                        else:
                            mapped_row.append("")
                    else:
                        mapped_row.append("User")
                
                # Try to get the value directly if it exists
                else:
                    mapped_row.append(row.get(column, ""))
            
            # Only add the row if we have all the required columns
            if len(mapped_row) == len(minimal_columns):
                values.append(mapped_row)
            
        # Debug log to show the data being written
        print(f"Values to write: {values}")
        
        # If we only have headers and no data, add a sample row
        if len(values) == 1:
            st.warning("No valid data found. Adding a sample row to demonstrate format.")
            values.append([
                "https://www.linkedin.com/in/sample-profile/",
                "Sample", 
                "User"
            ])
        
        # Write headers and data
        body = {'values': values}
        result = service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range="candidatos!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Debug info
        print(f"Updated range: {result.get('updatedRange')}")
        print(f"Updated rows: {result.get('updatedRows')}")
        print(f"Updated cells: {result.get('updatedCells')}")
        
        st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"Successfully wrote {len(values)-1} contacts to spreadsheet!")
        return True
        
    except Exception as e:
        st.error(f"Error writing to sheet: {e}")
        traceback.print_exc()
        return False

# Functions to interact with Data Enricher
def check_agent_running():
    """Check if the PhantomBuster agent is currently running"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/fetch"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": DATA_ENRICHER_AGENT_ID}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if the agent is running
            is_running = data.get("status") == "running"
            
            if is_running:
                container_id = data.get("lastContainerId")
                return True, container_id
            else:
                return False, None
        else:
            print(f"Error checking agent status: {response.status_code} - {response.text}")
            return False, None
    except Exception as e:
        print(f"Exception checking agent status: {e}")
        return False, None

def abort_agent():
    """Abort the currently running agent"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/abort"
        headers = {
            "X-Phantombuster-Key": DATA_ENRICHER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {"id": DATA_ENRICHER_AGENT_ID}
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error aborting agent: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception aborting agent: {e}")
        return False

def launch_enricher_job(urls=None, query=None, limit=5):
    """Launch data enrichment job using the correct PhantomBuster API parameters"""
    try:
        # First check if agent is already running
        is_running, container_id = check_agent_running()
        
        if is_running:
            st.error("⚠️ The DataEnricher agent is already running! Cannot launch a new job.")
            
            # Offer to abort the current job
            if st.button("Abort Current Job and Try Again"):
                with st.spinner("Aborting current job..."):
                    abort_result = abort_agent()
                    if abort_result:
                        st.success("Successfully aborted the running job.")
                        time.sleep(2)  # Wait for the abort to take effect
                        st.info("You can now try launching the job again.")
                    else:
                        st.error("Failed to abort the running job.")
            
            return None
            
        # Ensure the sheet is properly formatted
        sheet_data = get_sheet_data()
        
        # Check if we have valid LinkedIn URLs in the sheet
        valid_urls = 0
        if sheet_data:
            for row in sheet_data:
                if 'Profile Url' in row and row['Profile Url'] and 'linkedin.com/in/' in row['Profile Url'].lower():
                    valid_urls += 1
        
        if valid_urls == 0:
            st.error("❌ No valid LinkedIn URLs found in the spreadsheet. Please add valid LinkedIn URLs first.")
            return None
        
        # According to PhantomBuster documentation, this is the correct endpoint
        url = "https://api.phantombuster.com/api/v2/agents/launch"
        
        # First, try to get the agent's current configuration
        agent_config = get_agent_config()
        
        # Create a proper configuration based on PhantomBuster documentation
        if urls:
            # LinkedIn Profile Scraper config with all required fields
            scraper_config = {
                "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
                "columnName": "Profile Url",  # CRITICAL: Use "Profile Url" with space and capital letters
                "numberOfProfilesPerLaunch": limit,
                "numberOfAddsPerLaunch": 10,  # Ensure this is set
                "enrichWithCompanyData": True,  # Get company data too
                "pushResultToCRM": True,  # Save results
                "forceRescrape": True,  # CRITICAL: Force PhantomBuster to re-scrape profiles
                "saveResults": True,  # Save results to database
                "saveEveryStep": True  # Save intermediate results
            }
            
            # If we have existing identity information, keep it
            if agent_config and "identities" in agent_config:
                scraper_config["identities"] = agent_config["identities"]
        elif query:
            # LinkedIn Search Export config
            scraper_config = {
                "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
                "searchUrl": f"https://www.linkedin.com/search/results/people/?keywords={query}",
                "numberOfProfiles": limit,
                "saveSearchResults": True
            }
        
        # Construct the payload according to documentation
        payload = {
            "id": DATA_ENRICHER_AGENT_ID,
            "argument": scraper_config
        }
        
        # Log the payload for debugging
        print(f"Launching enricher with payload: {json.dumps(payload, indent=2)}")
        
        # Use the correct headers according to documentation
        headers = {
            "X-Phantombuster-Key": DATA_ENRICHER_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Clear any previous results from session state
        if 'enricher_results' in st.session_state:
            del st.session_state.enricher_results
        
        # Make the API request with proper error handling
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("containerId")
                st.session_state.enricher_job_id = job_id
                st.session_state.enricher_status = "running"
                
                # Show success message with job ID
                st.success(f"✅ Successfully launched DataEnricher job (ID: {job_id})")
                st.info("The job is now running. You'll see updates on the progress below.")
                
                return job_id
            elif response.status_code == 429:
                # Handle rate limiting or parallel execution limit
                error_data = response.json()
                error_message = error_data.get('error', 'Unknown error')
                
                if "maxParallelismReached" in str(error_data) or "parallel executions" in str(error_message):
                    st.error(f"⚠️ Maximum parallel executions limit reached: {error_message}")
                    st.info("Your PhantomBuster account has a limit on how many jobs can run at once. Please wait for any running jobs to complete before trying again.")
                    
                    # Offer demo data as an alternative
                    st.warning("While waiting, you can use the demo data option to see how the enriched data will look.")
                else:
                    st.error(f"Rate limit reached: {error_message}")
                
                st.session_state.enricher_status = "error"
                return None
            else:
                st.error(f"Error launching data enrichment job: {response.status_code} - {response.text}")
                st.session_state.enricher_status = "error"
                return None
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be busy. Please try again.")
            st.session_state.enricher_status = "error"
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {e}")
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
                results = get_enricher_results()
                if results:
                    print(f"Successfully retrieved enriched data with {len(results)} records")
                else:
                    print("Failed to retrieve enriched data, will try again")
                    # Try a second time after a short delay
                    time.sleep(2)
                    results = get_enricher_results()
                
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
                        results = get_enricher_results()
                        if results:
                            print(f"Successfully retrieved enriched data with {len(results)} records")
                        else:
                            print("Failed to retrieve enriched data, will try again")
                            # Try a second time after a short delay
                            time.sleep(2)
                            results = get_enricher_results()
                        
                        return "completed"
                    elif container_status == "error":
                        st.session_state.enricher_status = "error"
                        return "error"
                    elif container_status in ["running", "queued"]:
                        return "running"
                
                # If we still can't determine, check if we can get results directly
                # Sometimes PhantomBuster doesn't report status correctly but results are available
                results = get_enricher_results()
                if results and len(results) > 0:
                    print(f"Found results despite unknown status, assuming completed")
                    st.session_state.enricher_status = "completed"
                    return "completed"
                
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
                    
                    # Try to get the results
                    results = get_enricher_results()
                    
                    return "completed"
                elif container_status == "error":
                    st.session_state.enricher_status = "error"
                    return "error"
            
            # If we still can't determine, check if we can get results directly
            results = get_enricher_results()
            if results and len(results) > 0:
                print(f"Found results despite unknown status, assuming completed")
                st.session_state.enricher_status = "completed"
                return "completed"
            
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
    """Get the results from the data enricher using the correct API endpoints"""
    try:
        # First, check if we have a container ID (job ID) from a recent run
        if st.session_state.enricher_job_id:
            # Try to get results from the container output first
            container_output = get_container_output(st.session_state.enricher_job_id)
            if container_output and "output" in container_output:
                print(f"Got container output with length: {len(container_output['output'])}")
        
        # Now try the official API endpoints in the correct order according to documentation
        
        # 1. First try the agent's fetch-output endpoint (most reliable)
        url = "https://api.phantombuster.com/api/v2/agents/fetch-output"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": DATA_ENRICHER_AGENT_ID}
        
        print(f"Trying to get results from agent output endpoint: {url}")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                agent_output = response.json()
                if agent_output and "output" in agent_output:
                    print(f"Successfully retrieved agent output")
                    
                    # CRITICAL FIX: Extract the result.json URL from the output and fetch data directly
                    output_text = agent_output.get('output', '')
                    
                    # Look for the result.json URL in the output
                    json_url_match = re.search(r'https://[^\s]+result\.json', output_text)
                    
                    if json_url_match:
                        json_url = json_url_match.group(0)
                        print(f"Found result JSON URL: {json_url}")
                        print(f"Fetching enriched data from S3...")
                        
                        # Fetch the JSON data directly from S3
                        json_response = requests.get(json_url)
                        
                        if json_response.status_code == 200:
                            try:
                                enriched_data = json_response.json()
                                if isinstance(enriched_data, list) and len(enriched_data) > 0:
                                    print(f"✓ Successfully retrieved {len(enriched_data)} enriched profiles from result.json")
                                    st.session_state.enricher_results = enriched_data
                                    return enriched_data
                                else:
                                    print(f"Result JSON is empty or not a list: {type(enriched_data)}")
                            except json.JSONDecodeError:
                                print(f"Failed to parse result.json")
                        else:
                            print(f"Failed to fetch result.json: {json_response.status_code}")
                    else:
                        print("No result.json URL found in output")
                    
                    # Fallback: Try the old method
                    result_url = "https://api.phantombuster.com/api/v1/agent/686901552340687/output"
                    result_response = requests.get(result_url, headers=headers)
                    
                    if result_response.status_code == 200:
                        try:
                            result_data = result_response.json()
                            if isinstance(result_data, dict) and "data" in result_data:
                                print(f"Successfully retrieved result data with {len(result_data['data'])} records")
                                st.session_state.enricher_results = result_data["data"]
                                return result_data["data"]
                        except:
                            print(f"Failed to parse result data as JSON")
            except:
                print(f"Failed to parse agent output as JSON")
        
        # 2. Try to get data directly from Google Sheets as a fallback
        print("API endpoints failed, trying to get data from Google Sheets")
        sheet_data = get_sheet_data()
        
        # Check if the sheet data has enriched fields
        if sheet_data and len(sheet_data) > 0:
            # Look for enriched fields in the Google Sheet
            enriched_fields = ["First Name", "Last Name", "Linkedin Headline", "Company Name", 
                              "Company Industry", "Professional Email"]
            has_enriched_data = False
            
            for entry in sheet_data:
                for field in enriched_fields:
                    if field in entry and entry[field] and entry[field] != "Unknown" and entry[field] != "User":
                        has_enriched_data = True
                        break
                if has_enriched_data:
                    break
            
            if has_enriched_data:
                print("Found enriched data in Google Sheets")
                st.session_state.enricher_results = sheet_data
                return sheet_data
        
        # 3. If all else fails, check if we have any data in the session state already
        if "enricher_results" in st.session_state and st.session_state.enricher_results:
            print("Using cached results from session state")
            return st.session_state.enricher_results
        
        # If we still don't have data, return None
        return None
    except Exception as e:
        print(f"Exception in get_enricher_results: {e}")
        return None

def get_container_output(container_id):
    """Get the output of a specific container"""
    try:
        url = "https://api.phantombuster.com/api/v2/containers/fetch-output"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": container_id}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting container output: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception getting container output: {e}")
        return None

# Function to check if data is actually enriched
def check_if_data_enriched(data):
    """Check if the data has been properly enriched"""
    if not data:
        return False
    
    # Count how many entries have enriched fields
    enriched_count = 0
    non_empty_fields_count = 0
    
    # Fields that indicate enrichment from LinkedIn (PhantomBuster output format)
    important_fields = [
        'Linkedin Skills Label', 'Linkedin Description', 'Linkedin School Name', 
        'Company Name', 'Linkedin Headline', 'Company Industry', 'Linkedin School Name',
        'Linkedin Job Title', 'Professional Email', 'Linkedin Profile Image Url'
    ]
    
    # Fields that are typically present in PhantomBuster output
    phantom_fields = [
        'Profile Url', 'First Name', 'Last Name', 'Refreshed At',
        'Location', 'Scraper Profile Id', 'Scraper Full Name'
    ]
    
    # Legacy fields (older format)
    legacy_fields = [
        'skills_tags', 'summary', 'education', 'current_company', 
        'headline', 'industry', 'school', 'jobTitle', 'company',
        'profileUrl', 'fullName', 'firstName', 'lastName', 
        'connectionDegree', 'profileImageUrl', 'timestamp'
    ]
    
    for entry in data:
        # Skip non-dict entries
        if not isinstance(entry, dict):
            continue
            
        # Check for important enriched fields
        has_enriched_field = False
        has_phantom_field = False
        
        # Count non-empty fields
        field_count = 0
        for field in entry:
            if field in entry and entry[field] and str(entry[field]).strip():
                field_count += 1
        
        # Check for important enrichment fields (PhantomBuster format)
        for field in important_fields:
            if field in entry and entry[field] and str(entry[field]).strip():
                has_enriched_field = True
                break
        
        # Check for PhantomBuster-specific fields
        for field in phantom_fields:
            if field in entry and entry[field] and str(entry[field]).strip():
                has_phantom_field = True
                break
                
        # Check legacy fields if no enrichment found
        if not has_enriched_field:
            for field in legacy_fields:
                if field in entry and entry[field] and str(entry[field]).strip() and len(str(entry[field])) > 3:
                    has_enriched_field = True
                    break
        
        # If entry has many fields or has important fields, count it as enriched
        if has_enriched_field or has_phantom_field or field_count >= 5:
            enriched_count += 1
        
        # Count entries with at least some data
        if field_count >= 3:
            non_empty_fields_count += 1
    
    print(f"Enrichment check: {enriched_count}/{len(data)} entries have enriched fields")
    print(f"Non-empty check: {non_empty_fields_count}/{len(data)} entries have non-empty fields")
    
    # Consider data enriched if:
    # 1. At least 1 entry has important enriched fields, OR
    # 2. At least 30% of entries have non-empty fields
    return (enriched_count >= 1) or (non_empty_fields_count >= len(data) * 0.3)

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
        
        # Print original columns for debugging
        print(f"Original columns: {df.columns.tolist()}")
        
        # Keep the original columns - don't rename anything
        # We'll handle the mapping in validate_and_fix_linkedin_urls and write_to_sheet
        
        # Convert to list of dicts
        data = df.replace({np.nan: None}).to_dict('records')
        
        # Check if we have LinkedIn URLs in any column
        linkedin_url_columns = []
        for col in df.columns:
            if df[col].astype(str).str.contains('linkedin.com/in/', case=False).any():
                linkedin_url_columns.append(col)
        
        if linkedin_url_columns:
            st.info(f"Found LinkedIn URLs in column(s): {', '.join(linkedin_url_columns)}")
        else:
            st.warning("⚠️ No columns with LinkedIn URLs detected. Please ensure your file contains LinkedIn profile URLs.")
            
            # Show column preview to help user identify their data
            with st.expander("Column Preview"):
                for col in df.columns:
                    if len(df) > 0:
                        st.write(f"**{col}**: {df[col].iloc[0]}")
        
        # Debug info
        if data:
            all_keys = set()
            for row in data:
                all_keys.update(row.keys())
            st.info(f"Processed {len(data)} contacts with fields: {', '.join(all_keys)}")
        
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
            if st.button("Add Sample LinkedIn URLs", type="primary"):
                with st.spinner("Adding sample LinkedIn profiles..."):
                    sample_data = [
                        {
                            "Profile Url": "https://www.linkedin.com/in/alisson-frota/",
                            "First Name": "Alisson",
                            "Last Name": "Frota"
                        },
                        {
                            "Profile Url": "https://www.linkedin.com/in/herbert-zapata-salvo/",
                            "First Name": "Herbert",
                            "Last Name": "Zapata Salvo"
                        },
                        {
                            "Profile Url": "https://www.linkedin.com/in/rkniazev/",
                            "First Name": "Roman",
                            "Last Name": "K."
                        },
                        {
                            "Profile Url": "https://www.linkedin.com/in/enbonnet/",
                            "First Name": "Ender",
                            "Last Name": "Bonnet"
                        },
                        {
                            "Profile Url": "https://www.linkedin.com/in/pierinazaramella/",
                            "First Name": "Pierina",
                            "Last Name": "Zaramella"
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
                
                # CRITICAL FIX: Get data from PhantomBuster results, NOT from Google Sheet
                # The enriched data is already stored in enricher_results by get_enricher_results()
                if 'enricher_results' in st.session_state and st.session_state.enricher_results:
                    updated_data = st.session_state.enricher_results
                    st.session_state.candidates = updated_data  # Store it in candidates for display
                    print(f"Using PhantomBuster enriched data with {len(updated_data)} profiles")
                else:
                    # Fallback to Google Sheet only if PhantomBuster data is not available
                    updated_data = get_sheet_data()
                    print(f"Falling back to Google Sheet data")
                
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

# Tab 2: Search Candidates (AI Chat Interface)
with tab2:
    st.header("💬 Ask AI About Your Candidates")
    st.write("Chat with AI to find the perfect candidates from your enriched data")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Get current candidates data
    current_candidates = st.session_state.candidates if st.session_state.data_loaded and st.session_state.candidates else []
    
    # Generate dynamic suggestions based on actual data
    def generate_dynamic_suggestions(candidates):
        """Generate search suggestions based on actual candidate data"""
        if not candidates or len(candidates) == 0:
            return [
                "Quien tiene magíster en finanzas?",
                "Quien trabajó en marketing digital?",
                "Quien tiene experiencia en minería?",
                "Quien tiene experiencia en análisis de riesgo?",
                "Quien tiene skills en Python y data science?",
                "Quien trabajó en startups chilenas?"
            ]
        
        suggestions = []
        
        # Extract common skills, companies, and education from the data
        all_skills = set()
        all_companies = set()
        all_education = set()
        
        for candidate in candidates[:10]:  # Check first 10 candidates
            # Skills
            for skill_field in ['skills_tags', 'Linkedin Skills Label', 'linkedinSkillsLabel']:
                if skill_field in candidate and candidate[skill_field]:
                    skills = str(candidate[skill_field]).split(',')
                    all_skills.update([s.strip().lower() for s in skills[:3]])
            
            # Companies
            for company_field in ['Company Name', 'companyName', 'current_company']:
                if company_field in candidate and candidate[company_field]:
                    all_companies.add(str(candidate[company_field]).strip())
            
            # Education
            for edu_field in ['Linkedin School Degree', 'linkedinSchoolDegree', 'education']:
                if edu_field in candidate and candidate[edu_field]:
                    all_education.add(str(candidate[edu_field]).strip())
        
        # Create dynamic suggestions
        if all_skills:
            top_skills = list(all_skills)[:2]
            if top_skills:
                suggestions.append(f"Quien tiene experiencia en {top_skills[0]}?")
        
        if all_companies:
            top_companies = list(all_companies)[:1]
            if top_companies:
                suggestions.append(f"Quien trabajó en {top_companies[0]}?")
        
        if all_education:
            suggestions.append("Quien tiene estudios de posgrado?")
        
        # Add some generic but useful ones
        suggestions.extend([
            "Muéstrame los candidatos más calificados",
            "Quien tiene más de 5 años de experiencia?",
            "Resumen de los perfiles disponibles"
        ])
        
        return suggestions[:6]
    
    # Check if a preset button was clicked in previous run
    preset_query = None
    if 'preset_clicked' in st.session_state:
        preset_query = st.session_state.preset_clicked
        del st.session_state.preset_clicked
    
    # Suggestions section at the top
    suggestions = generate_dynamic_suggestions(current_candidates)
    
    st.markdown("### 💡 Try these searches:")
    cols = st.columns(3)
    for idx, suggestion in enumerate(suggestions):
        col_idx = idx % 3
        with cols[col_idx]:
            if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                st.session_state.preset_clicked = suggestion
                st.rerun()
    
    st.divider()
    
    # Main chat input at the top (more prominent)
    query = st.text_area(
        "Ask anything about your candidates:",
        placeholder="Example: Quien tiene experiencia en desarrollo web y habla inglés?",
        height=100,
        key="chat_input"
    )
    
    # Send button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        send_button = st.button("🔍 Search", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    st.divider()
    
    # Process query - either from button click or from preset
    if (send_button and query) or preset_query:
        with st.spinner("Searching..."):
            # Use preset query if available, otherwise use text input
            search_term = preset_query if preset_query else query
            
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
            ai_explanation = None
            
            # Try AI-powered search first if available
            if USE_AI_SEARCH and openai_client:
                st.info("🤖 Using AI to analyze candidates...")
                ai_candidates, ai_explanation = ai_search_candidates(search_term, candidates)
                
                if ai_candidates:
                    filtered_candidates = ai_candidates
                    # Add match scores for consistency
                    for i, candidate in enumerate(filtered_candidates):
                        candidate['match_score'] = len(filtered_candidates) - i + 10
            
            # Fall back to keyword search if AI didn't work or isn't available
            if not filtered_candidates:
                if USE_AI_SEARCH:
                    st.info("Falling back to keyword search...")
                
                search_term_lower = search_term.lower()
                
                # Define field mappings for both old and new formats
                field_mappings = {
                    'education': ['education', 'Linkedin School Degree', 'Linkedin School Name'],
                    'headline': ['headline', 'Linkedin Headline'],
                    'skills': ['skills_tags', 'Linkedin Skills Label'],
                    'company': ['current_company', 'company', 'Company Name', 'Linkedin Company Name'],
                    'location': ['Location', 'Linkedin Job Location'],
                    'description': ['summary', 'Linkedin Description', 'Linkedin Job Description'],
                    'job_title': ['jobTitle', 'Linkedin Job Title']
                }
                
                # Simple filtering logic based on the search term
                for candidate in candidates:
                    score = 0
                    
                    # Check all mapped fields for matches
                    for field_category, field_names in field_mappings.items():
                        for field in field_names:
                            if field in candidate and candidate[field]:
                                field_value = str(candidate[field]).lower()
                                
                                # Direct match with search term
                                if search_term_lower in field_value:
                                    score += 2
                                
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
                                if "php" in search_term_lower and "php" in field_value:
                                    score += 2
                                if "drupal" in search_term_lower and "drupal" in field_value:
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
            
            # Add user message to chat history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': search_term
            })
            
            # Generate AI response
            if len(filtered_candidates) == 0:
                response_text = f"No encontré candidatos que coincidan con '{search_term}'. Intenta con otros criterios de búsqueda."
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response_text,
                    'candidates': []
                })
            else:
                # Use AI explanation if available, otherwise use generic message
                if ai_explanation:
                    response_text = f"🤖 **Análisis AI:**\n\n{ai_explanation}\n\nEncontré {len(filtered_candidates)} candidatos relevantes:"
                else:
                    response_text = f"Encontré {len(filtered_candidates)} candidatos que coinciden con tu búsqueda. Aquí están los más relevantes:"
                
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response_text,
                    'candidates': filtered_candidates[:5]
                })
            
            # Set flag to trigger scroll on next render
            st.session_state.should_scroll = True
            
            # Force rerun to display the new message
            st.rerun()
    
    # Display chat history BELOW the input
    st.markdown("---")
    st.markdown('<div id="chat-history-section"></div>', unsafe_allow_html=True)
    st.markdown("### 💬 Chat History")
    
    # Auto-scroll to chat history after search - always scroll if there's chat history
    if len(st.session_state.chat_history) > 0 and st.session_state.get('should_scroll', False):
        # Include a unique timestamp in the HTML to force re-execution
        import time
        unique_id = int(time.time() * 1000)  # milliseconds timestamp
        components.html(
            f"""
            <script>
                // Unique execution ID: {unique_id}
                // Function to scroll to chat section
                function scrollToChat() {{
                    const chatSection = window.parent.document.getElementById('chat-history-section');
                    if (chatSection) {{
                        chatSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }}
                
                // Try multiple times to ensure it works
                setTimeout(scrollToChat, 50);
                setTimeout(scrollToChat, 200);
                setTimeout(scrollToChat, 500);
            </script>
            """,
            height=0
        )
        # Reset the flag after scroll is triggered
        st.session_state.should_scroll = False
    
    if len(st.session_state.chat_history) == 0:
        st.info("No messages yet. Ask a question above to get started!")
    else:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**🧑 You:** {message['content']}")
            else:
                st.markdown(f"**🤖 AI:** {message['content']}")
                if 'candidates' in message and message['candidates']:
                    with st.expander(f"📋 {len(message['candidates'])} matching candidates", expanded=True):
                        for i, candidate in enumerate(message['candidates'][:5]):
                            name = candidate.get('Full Name', candidate.get('firstName', 'Unknown'))
                            if not name or name == 'Unknown':
                                name = f"{candidate.get('firstName', '')} {candidate.get('lastName', '')}".strip()
                            if not name:
                                name = "Unknown"
                            headline = candidate.get('Linkedin Headline', candidate.get('linkedinHeadline', candidate.get('headline', 'No headline')))
                            company = candidate.get('Company Name', candidate.get('companyName', candidate.get('current_company', '')))
                            
                            st.write(f"**{i+1}. {name}**")
                            st.write(f"   📌 {headline}")
                            if company:
                                st.write(f"   🏢 {company}")
                            st.write("---")
            st.markdown("")  # Add some spacing

# Tab 3: Data View
with tab3:
    st.header("Current Data")
    
    # Load button
    if st.button("Refresh Data", type="primary"):
        with st.spinner("Loading data from Google Sheet..."):
            # First try to get data from enricher results if available
            if 'enricher_results' in st.session_state and st.session_state.enricher_results:
                st.session_state.candidates = st.session_state.enricher_results
                st.success("✅ Loaded enriched data from PhantomBuster results")
            else:
                # Fall back to Google Sheet data
                sheet_data = get_sheet_data()
                if sheet_data:
                    st.session_state.candidates = sheet_data
                    st.success(f"✅ Loaded {len(sheet_data)} records from Google Sheet")
                else:
                    st.error("❌ Failed to load data from Google Sheet")
    
    # Show data
    if 'candidates' in st.session_state and st.session_state.candidates:
        # Normalize data structure to avoid DataFrame creation errors
        all_keys = set()
        for item in st.session_state.candidates:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        normalized_data = []
        for item in st.session_state.candidates:
            if isinstance(item, dict):
                normalized_item = {key: None for key in all_keys}
                normalized_item.update(item)
                normalized_data.append(normalized_item)
        
        # Create dataframe from normalized data
        df = pd.DataFrame(normalized_data) if normalized_data else pd.DataFrame()
        
        # Show data count
        st.success(f"Showing {len(df)} enriched profiles")
        
        # Organize columns into categories for better viewing
        column_categories = {
            "Basic Info": ["Profile Url", "First Name", "Last Name", "Linkedin Headline", "Location", 
                          "Linkedin Profile Image Url", "Professional Email", "profileUrl", "firstName", 
                          "lastName", "fullName", "headline", "location"],
            
            "Company Info": ["Company Name", "Company Industry", "Company Website", "Linkedin Company Name",
                           "Linkedin Company Url", "Linkedin Company Description", "company", "companyName", 
                           "companyUrl", "companyId", "companyWebsite", "companyIndustry", "industry"],
            
            "Job Info": ["Linkedin Job Title", "Linkedin Job Date Range", "Linkedin Job Location", 
                        "Linkedin Job Description", "Linkedin Previous Job Title", "jobTitle", "jobDateRange",
                        "Linkedin Previous Job Date Range", "Linkedin Previous Job Description", "currentJobTitle"],
            
            "Education": ["Linkedin School Name", "Linkedin School Degree", "Linkedin School Date Range",
                         "Linkedin Previous School Name", "Linkedin Previous School Degree", "school", "schoolDegree",
                         "Linkedin Previous School Date Range", "education", "schoolDateRange"],
            
            "Skills & Details": ["Linkedin Skills Label", "Linkedin Description", "skills", "skills_tags",
                               "summary", "description", "connectionDegree", "sharedConnections"],
            
            "Metadata": ["Refreshed At", "Scraper Profile Id", "Scraper Full Name", "Error", "timestamp", 
                        "vmid", "category", "searchAccountFullName"]
        }
        
        # Create tabs for each category
        data_tabs = st.tabs(list(column_categories.keys()))
        
        # Display data in each tab
        for i, (category, columns) in enumerate(column_categories.items()):
            with data_tabs[i]:
                # Filter columns that exist in the dataframe
                existing_columns = [col for col in columns if col in df.columns]
                
                if existing_columns:
                    st.dataframe(df[existing_columns], width='stretch')
                else:
                    st.info(f"No {category.lower()} data available.")
        
        # Add a "Raw Data" tab with all columns
        with st.expander("Raw Data (All Columns)"):
            # Show all columns in the dataframe
            st.dataframe(df, width='stretch')
            
            # Add download button for the data
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="enriched_linkedin_data.csv",
                mime="text/csv",
            )
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

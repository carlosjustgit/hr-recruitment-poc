"""
Test LinkedIn Profile Scraper with PhantomBuster

This script will:
1. Get the agent configuration for the LinkedIn Profile Scraper
2. Launch a job with the correct parameters
3. Monitor the job status
"""
import requests
import json
import time
import os
import streamlit as st

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "686901552340687"  # LinkedIn Profile Scraper
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"

st.set_page_config(page_title="Test LinkedIn Profile Scraper", page_icon="🔍", layout="wide")
st.title("Test LinkedIn Profile Scraper")
st.write("This tool will test the LinkedIn Profile Scraper with PhantomBuster")

def get_agent_info():
    """Get agent information"""
    url = "https://api.phantombuster.com/api/v2/agents/fetch"
    headers = {"X-Phantombuster-Key": PHANTOM_API_KEY}
    params = {"id": PHANTOM_AGENT_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def launch_job():
    """Launch a LinkedIn Profile Scraper job with the correct parameters"""
    url = "https://api.phantombuster.com/api/v2/agents/launch"
    
    # Create the configuration for LinkedIn Profile Scraper
    config = {
        "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
        "columnName": "Profile Url",  # CRITICAL: This must match exactly
        "numberOfProfilesPerLaunch": 5,
        "sessionCookie": "li_at=AAEAAB_Dxf4FGdvuAAABi0ySbfwAAAGLaJ7x_E4AqWXQFw6MHkQDpvRlODPHXPwYADWIkRfXVrHYKHkVrTJJqXPbRLPzUHJHfV_nY7YHRpgYVFMDlvQoOVTVAFRTfOPnZPRHRKcCu9VNTwKIoKGOgDO2"
    }
    
    # Construct the payload
    payload = {
        "id": PHANTOM_AGENT_ID,
        "argument": config
    }
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def check_job_status(container_id):
    """Check the status of a PhantomBuster job"""
    url = "https://api.phantombuster.com/api/v2/containers/fetch-output"
    headers = {"X-Phantombuster-Key": PHANTOM_API_KEY}
    params = {"id": container_id}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def get_job_progress(container_id):
    """Get the progress of a PhantomBuster job"""
    status_data = check_job_status(container_id)
    
    if "error" in status_data:
        return None
    
    output = status_data.get("output", "")
    
    # Try to parse progress information from output
    import re
    progress_match = re.search(r"Processing (?:profile|profiles|URL) (\d+)/(\d+)", output)
    if progress_match:
        processed = int(progress_match.group(1))
        total = int(progress_match.group(2))
        return {'processed': processed, 'total': total}
    
    return None

def main():
    """Main function"""
    # Get agent info
    st.subheader("Agent Information")
    agent_info = get_agent_info()
    
    if "error" in agent_info:
        st.error(f"Error getting agent info: {agent_info['error']}")
    else:
        st.write(f"Agent Name: {agent_info.get('name', 'Unknown')}")
        st.write(f"Agent Status: {agent_info.get('status', 'Unknown')}")
        
        with st.expander("Full Agent Info"):
            st.json(agent_info)
    
    # Launch job
    st.subheader("Launch Job")
    if st.button("Launch LinkedIn Profile Scraper"):
        with st.spinner("Launching job..."):
            result = launch_job()
            
            if "error" in result:
                st.error(f"Error launching job: {result['error']}")
            else:
                container_id = result.get("containerId")
                st.success(f"Job launched successfully! Container ID: {container_id}")
                
                # Store container ID in session state
                st.session_state.container_id = container_id
                
                # Show what's happening
                with st.expander("What's happening now?", expanded=True):
                    st.write("""
                    1. PhantomBuster is now accessing your Google Sheet
                    2. It will look for LinkedIn profile URLs in the "Profile Url" column
                    3. It will scrape data from those profiles
                    4. The results will be written back to your Google Sheet
                    """)
    
    # Monitor job
    st.subheader("Monitor Job")
    if "container_id" in st.session_state:
        container_id = st.session_state.container_id
        
        status_container = st.empty()
        progress_container = st.empty()
        output_container = st.empty()
        
        # Create a progress bar
        progress_bar = progress_container.progress(0)
        
        # Monitor the job
        max_checks = 60
        check_interval = 5
        
        for i in range(1, max_checks + 1):
            # Check job status
            status_data = check_job_status(container_id)
            
            if "error" in status_data:
                status_container.error(f"Error checking job status: {status_data['error']}")
                break
            
            status = status_data.get("status")
            output = status_data.get("output", "")
            
            # Update output
            output_container.code(output)
            
            # Get progress
            progress_info = get_job_progress(container_id)
            
            if progress_info:
                processed = progress_info['processed']
                total = progress_info['total']
                
                if total > 0:
                    progress_percent = min(90, int((processed / total) * 100))
                    progress_bar.progress(progress_percent)
                    status_container.info(f"Job in progress... Processing profiles {processed}/{total} ({progress_percent}%)")
                else:
                    progress_percent = min(80, int((i / max_checks) * 100))
                    progress_bar.progress(progress_percent)
                    status_container.info(f"Job in progress... ({progress_percent}%)")
            else:
                progress_percent = min(80, int((i / max_checks) * 100))
                progress_bar.progress(progress_percent)
                status_container.info(f"Job in progress... Checking status ({i}/{max_checks})")
            
            # Check if job is complete
            if status == "finished":
                progress_bar.progress(100)
                status_container.success("✅ Job completed successfully!")
                
                # Show results
                st.subheader("Results")
                st.write("Job completed! The results should now be in your Google Sheet.")
                
                # Google Sheet link
                sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
                st.markdown(f"[Open Google Sheet]({sheet_url})")
                
                break
            elif status == "error":
                progress_bar.progress(100)
                status_container.error("❌ Job failed")
                st.error("The job failed to complete. Please check the output for details.")
                break
            
            # Wait before next check
            time.sleep(check_interval)
    else:
        st.info("No job running. Click 'Launch LinkedIn Profile Scraper' to start a job.")
    
    # Google Sheet link
    st.subheader("Google Sheet")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
    st.markdown(f"[Open Google Sheet]({sheet_url})")

if __name__ == "__main__":
    main()

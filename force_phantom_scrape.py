"""
Force PhantomBuster to re-scrape LinkedIn profiles by using the forceRescrape parameter
"""
import requests
import json
import time
import streamlit as st

# Configuration
API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
AGENT_ID = "686901552340687"
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"

def main():
    st.title("Force PhantomBuster to Re-Scrape Profiles")
    
    # First check if agent is already running
    is_running, container_id = check_agent_running()
    
    if is_running:
        st.error("⚠️ The agent is currently running! Please wait for it to complete or abort it.")
        
        # Show abort option
        if st.button("Abort Running Job"):
            abort_result = abort_agent()
            if abort_result:
                st.success("Successfully aborted the running job.")
                st.rerun()
            else:
                st.error("Failed to abort the running job.")
    else:
        st.success("✅ Agent is not running. You can launch a new job.")
        
        # Options for the scraper
        st.subheader("Scraper Options")
        
        # Force rescrape option
        force_rescrape = st.checkbox("Force Re-Scrape Profiles", value=True, 
                                    help="Enable this to force PhantomBuster to re-scrape profiles even if they were recently scraped")
        
        # Number of profiles to scrape
        num_profiles = st.slider("Number of Profiles to Scrape", min_value=1, max_value=10, value=5)
        
        # Launch button
        if st.button("Launch LinkedIn Profile Scraper", type="primary"):
            with st.spinner("Launching scraper..."):
                result = launch_agent(force_rescrape=force_rescrape, num_profiles=num_profiles)
                if result:
                    st.success(f"✅ Successfully launched job with ID: {result}")
                    
                    # Show link to PhantomBuster console
                    phantom_url = f"https://phantombuster.com/console/agents/{AGENT_ID}"
                    st.markdown(f"[View job in PhantomBuster Console]({phantom_url})")
                else:
                    st.error("❌ Failed to launch job")

def check_agent_running():
    """Check if the agent is currently running"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/fetch"
        headers = {"X-Phantombuster-Key": API_KEY}
        params = {"id": AGENT_ID}
        
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
            st.error(f"Error checking agent status: {response.status_code} - {response.text}")
            return False, None
    except Exception as e:
        st.error(f"Exception checking agent status: {e}")
        return False, None

def abort_agent():
    """Abort the currently running agent"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/abort"
        headers = {
            "X-Phantombuster-Key": API_KEY,
            "Content-Type": "application/json"
        }
        payload = {"id": AGENT_ID}
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error aborting agent: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Exception aborting agent: {e}")
        return False

def launch_agent(force_rescrape=True, num_profiles=5):
    """Launch the LinkedIn Profile Scraper agent with force rescrape option"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/launch"
        
        # Get agent's current configuration first
        agent_config = get_agent_config()
        
        # Prepare the configuration
        config = {
            "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
            "columnName": "Profile Url",  # CRITICAL: Use "Profile Url" with space and capital letters
            "numberOfProfiles": num_profiles,
            "numberOfAddsPerLaunch": 10,
            "enrichWithCompanyData": True,
            "pushResultToCRM": True,
            "forceRescrape": force_rescrape  # CRITICAL: This forces PhantomBuster to re-scrape profiles
        }
        
        # Update with existing identity information if available
        if agent_config and "identities" in agent_config:
            config["identities"] = agent_config["identities"]
        
        # Construct the payload
        payload = {
            "id": AGENT_ID,
            "argument": config
        }
        
        # Log the payload for debugging
        st.code(json.dumps(payload, indent=2))
        
        headers = {
            "X-Phantombuster-Key": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("containerId")
        elif response.status_code == 429:
            # Handle rate limiting or parallel execution limit
            error_data = response.json()
            st.error(f"Rate limit or parallel execution limit reached: {error_data.get('error')}")
            return None
        else:
            st.error(f"Error launching agent: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception launching agent: {e}")
        return None

def get_agent_config():
    """Get the agent's current configuration"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/fetch"
        headers = {"X-Phantombuster-Key": API_KEY}
        params = {"id": AGENT_ID}
        
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

if __name__ == "__main__":
    main()

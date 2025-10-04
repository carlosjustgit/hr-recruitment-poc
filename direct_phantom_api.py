"""
Direct PhantomBuster API integration with proper error handling
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
    st.title("PhantomBuster Direct API Test")
    
    # Check agent status first
    if st.button("Check Agent Status", type="primary"):
        with st.spinner("Checking agent status..."):
            status = check_agent_status()
            if status.get("isRunning"):
                st.error("⚠️ Agent is currently running! Cannot launch a new job until it completes.")
                
                # Show abort option
                if st.button("Abort Running Job"):
                    abort_result = abort_agent()
                    if abort_result:
                        st.success("Successfully aborted the running job.")
                    else:
                        st.error("Failed to abort the running job.")
            else:
                st.success("✅ Agent is not running. You can launch a new job.")
                
                # Show launch option
                if st.button("Launch LinkedIn Profile Scraper"):
                    result = launch_agent()
                    if result:
                        st.success(f"✅ Successfully launched job with ID: {result}")
                    else:
                        st.error("❌ Failed to launch job")

def check_agent_status():
    """Check if the agent is currently running"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/fetch"
        headers = {"X-Phantombuster-Key": API_KEY}
        params = {"id": AGENT_ID}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Display agent information
            st.info(f"Agent Name: {data.get('name')}")
            st.info(f"Agent Type: {data.get('scriptName')}")
            
            # Check if the agent is running
            is_running = data.get("status") == "running"
            
            if is_running:
                st.warning("⚠️ Agent is currently running!")
                
                # Get container info for more details
                container_id = data.get("lastContainerId")
                if container_id:
                    container_info = get_container_info(container_id)
                    if container_info:
                        st.info(f"Container ID: {container_id}")
                        st.info(f"Container Status: {container_info.get('status')}")
                        st.info(f"Started At: {container_info.get('startedAt')}")
            else:
                st.success("✅ Agent is not running")
                
            return {
                "isRunning": is_running,
                "containerId": data.get("lastContainerId"),
                "name": data.get("name")
            }
        else:
            st.error(f"Error checking agent status: {response.status_code} - {response.text}")
            return {"isRunning": False}
    except Exception as e:
        st.error(f"Exception checking agent status: {e}")
        return {"isRunning": False}

def get_container_info(container_id):
    """Get container info"""
    try:
        url = "https://api.phantombuster.com/api/v2/containers/fetch"
        headers = {"X-Phantombuster-Key": API_KEY}
        params = {"id": container_id}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error getting container info: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception getting container info: {e}")
        return None

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

def launch_agent():
    """Launch the LinkedIn Profile Scraper agent with correct parameters"""
    try:
        url = "https://api.phantombuster.com/api/v2/agents/launch"
        
        # Get agent's current configuration first
        agent_config = get_agent_config()
        
        # Prepare the configuration
        config = {
            "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
            "columnName": "Profile Url",  # CRITICAL: Use "Profile Url" with space and capital letters
            "numberOfProfiles": 5,
            "numberOfAddsPerLaunch": 10,
            "enrichWithCompanyData": True,
            "pushResultToCRM": True
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
            
            # Check if it's a parallel execution limit
            if "maxParallelismReached" in str(error_data):
                st.warning("⚠️ The agent is already running. You must wait for it to complete or abort it.")
                
                # Offer to abort the current job
                if st.button("Abort Current Job and Try Again"):
                    abort_result = abort_agent()
                    if abort_result:
                        st.success("Successfully aborted the running job.")
                        time.sleep(2)  # Wait for the abort to take effect
                        
                        # Try launching again
                        st.info("Trying to launch again...")
                        return launch_agent()
                    else:
                        st.error("Failed to abort the running job.")
            
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

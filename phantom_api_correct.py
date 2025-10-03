"""
PhantomBuster API Integration - Correct Implementation
Based on official PhantomBuster documentation
"""
import requests
import json
import time
import os
from datetime import datetime

# Configuration
API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
AGENT_ID = "686901552340687"  # LinkedIn Profile Scraper
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

def get_agent_info():
    """Get agent information to understand its configuration"""
    print("\n=== Getting Agent Info ===")
    
    url = "https://api.phantombuster.com/api/v2/agents/fetch"
    headers = {"X-Phantombuster-Key": API_KEY}
    params = {"id": AGENT_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Agent name: {data.get('name')}")
            print(f"Agent script: {data.get('script')}")
            
            # Extract and parse the argument JSON
            try:
                argument_str = data.get('argument', '{}')
                argument = json.loads(argument_str)
                print("\nCurrent agent configuration:")
                print(json.dumps(argument, indent=2))
                
                # Save to file for reference
                with open("agent_config.json", "w") as f:
                    json.dump(argument, f, indent=2)
                print("Configuration saved to agent_config.json")
                
                return argument
            except Exception as e:
                print(f"Error parsing argument: {e}")
                print(f"Raw argument: {argument_str}")
                return {}
        else:
            print(f"Error: {response.text}")
            return {}
    except Exception as e:
        print(f"Exception: {e}")
        return {}

def launch_agent():
    """Launch the LinkedIn Profile Scraper agent using the correct parameters"""
    print("\n=== Launching LinkedIn Profile Scraper ===")
    
    # According to documentation, we should use the agent's existing configuration
    # and only modify what we need
    agent_config = get_agent_info()
    
    # If we couldn't get the config, use a minimal default
    if not agent_config:
        agent_config = {
            "spreadsheetUrl": SHEET_URL,
            "columnName": "profileUrl",  # FIXED: Use profileUrl instead of linkedin_url
            "numberOfProfilesPerLaunch": 2
        }
    else:
        # Update only necessary fields
        agent_config["spreadsheetUrl"] = SHEET_URL
    
    # Construct payload according to documentation
    payload = {
        "id": AGENT_ID,
        "argument": agent_config
    }
    
    url = "https://api.phantombuster.com/api/v2/agents/launch"
    headers = {
        "X-Phantombuster-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print("\nSending payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            container_id = data.get("containerId")
            print(f"Success! Container ID: {container_id}")
            return container_id
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def check_container_status(container_id):
    """Check the status of a running container"""
    print(f"\n=== Checking Container Status: {container_id} ===")
    
    url = "https://api.phantombuster.com/api/v2/containers/fetch-output"
    headers = {"X-Phantombuster-Key": API_KEY}
    params = {"id": container_id}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print(f"Container status: {status}")
            
            # Save output to file
            with open(f"container_output_{container_id}.json", "w") as f:
                json.dump(data, f, indent=2)
            print(f"Output saved to container_output_{container_id}.json")
            
            return status
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def monitor_container(container_id, max_checks=10, interval=10):
    """Monitor a container until it finishes or max checks is reached"""
    if not container_id:
        print("No container ID provided")
        return False
    
    print(f"\n=== Monitoring Container: {container_id} ===")
    print(f"Will check status {max_checks} times with {interval} second intervals")
    
    for i in range(max_checks):
        print(f"\nCheck {i+1}/{max_checks}:")
        status = check_container_status(container_id)
        
        if status == "finished":
            print("Container finished successfully!")
            return True
        elif status == "error":
            print("Container finished with error")
            return False
        
        if i < max_checks - 1:
            print(f"Waiting {interval} seconds before next check...")
            time.sleep(interval)
    
    print("Maximum checks reached, container may still be running")
    return None

def get_agent_results():
    """Get the results of the agent (the data it has collected)"""
    print("\n=== Getting Agent Results ===")
    
    url = "https://api.phantombuster.com/api/v2/agents/fetch-json-result"
    headers = {"X-Phantombuster-Key": API_KEY}
    params = {"id": AGENT_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Save results to file
                with open("agent_results.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("Results saved to agent_results.json")
                
                # Print summary
                if isinstance(data, list):
                    print(f"Found {len(data)} results")
                    if len(data) > 0:
                        print("\nFirst result:")
                        print(json.dumps(data[0], indent=2)[:500])
                        print("...")
                else:
                    print("No results or unexpected format")
                
                return data
            except Exception as e:
                print(f"Error processing response: {e}")
                print(f"Raw response: {response.text[:500]}")
                return None
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    print("=== PhantomBuster API - LinkedIn Profile Scraper ===")
    print(f"API Key: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Sheet URL: {SHEET_URL}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # First, get agent info to understand its configuration
    get_agent_info()
    
    # Ask user if they want to launch the agent
    launch = input("\nLaunch the LinkedIn Profile Scraper? (y/n): ").strip().lower()
    if launch == 'y':
        # Launch the agent
        container_id = launch_agent()
        
        if container_id:
            # Ask if user wants to monitor the agent
            monitor = input("\nMonitor the agent until completion? (y/n): ").strip().lower()
            if monitor == 'y':
                success = monitor_container(container_id)
                
                if success:
                    # Get the results
                    get_results = input("\nGet the agent results? (y/n): ").strip().lower()
                    if get_results == 'y':
                        get_agent_results()
    
    print("\n=== Script Complete ===")

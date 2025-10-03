"""
Debug script for PhantomBuster API integration
This script will try different methods of launching a PhantomBuster job
"""
import requests
import json
import time
import os
from datetime import datetime

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "686901552340687"  # New agent ID
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

def get_agent_info():
    """Get detailed agent info"""
    print("\n=== Getting Agent Info ===")
    url = f"https://api.phantombuster.com/api/v2/agents/fetch"
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    params = {"id": PHANTOM_AGENT_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Agent name: {data.get('name')}")
            print(f"Agent script: {data.get('script')}")
            
            # Extract the argument JSON
            argument_str = data.get('argument', '{}')
            try:
                argument = json.loads(argument_str)
                print("\nCurrent agent configuration:")
                print(json.dumps(argument, indent=2))
                return argument
            except:
                print(f"Could not parse argument: {argument_str}")
                return {}
        else:
            print(f"Error: {response.text}")
            return {}
    except Exception as e:
        print(f"Exception: {e}")
        return {}

def try_launch_method_1():
    """Try launching with minimal parameters"""
    print("\n=== Trying Launch Method 1: Minimal Parameters ===")
    url = "https://api.phantombuster.com/api/v2/agents/launch"
    
    payload = {
        "id": PHANTOM_AGENT_ID
    }
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("containerId")
            print(f"Success! Job ID: {job_id}")
            return job_id
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def try_launch_method_2(agent_config):
    """Try launching with full agent configuration"""
    print("\n=== Trying Launch Method 2: Full Configuration ===")
    url = "https://api.phantombuster.com/api/v2/agents/launch"
    
    # Use the agent's existing configuration but update spreadsheet URL
    if isinstance(agent_config, dict):
        agent_config["spreadsheetUrl"] = SHEET_URL
    
    payload = {
        "id": PHANTOM_AGENT_ID,
        "argument": agent_config
    }
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print("Sending payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("containerId")
            print(f"Success! Job ID: {job_id}")
            return job_id
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def try_launch_method_3():
    """Try launching with specific LinkedIn Profile Scraper parameters"""
    print("\n=== Trying Launch Method 3: LinkedIn Profile Scraper Specific ===")
    url = "https://api.phantombuster.com/api/v2/agents/launch"
    
    # These are the exact parameters expected by LinkedIn Profile Scraper
    payload = {
        "id": PHANTOM_AGENT_ID,
        "argument": {
            "spreadsheetUrl": SHEET_URL,
            "columnName": "linkedin_url",
            "numberOfProfilesPerLaunch": 2,
            "csvName": "result",
            "noDatabase": False,
            "extractDefaultUrl": False,
            "removeDuplicateProfiles": False,
            "accountsToScrape": [],  # Will be taken from spreadsheet
            "sessionCookie": "AQEDAQIz2iQB2px0AAABmXZj66kAAAGZv9QVfFYAY2195-hn04on5tSbhyMAGBM0zAaXxgTJa5ruOr_BgGwwrIiAJVnQDmeFd_qVXlYm5-LrgFxBDu-rO2YZTnU8UxycwmKmqvipU62mCtq1sp_8z8zC"
        }
    }
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print("Sending payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("containerId")
            print(f"Success! Job ID: {job_id}")
            return job_id
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def check_job_status(job_id):
    """Check job status and wait for completion"""
    if not job_id:
        print("No job ID provided")
        return
    
    print(f"\n=== Checking Status for Job {job_id} ===")
    url = f"https://api.phantombuster.com/api/v2/containers/fetch-output"
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    params = {"id": job_id}
    
    max_checks = 10
    check_interval = 5  # seconds
    
    for i in range(max_checks):
        try:
            print(f"\nCheck {i+1}/{max_checks}:")
            response = requests.get(url, params=params, headers=headers)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                print(f"Job status: {status}")
                
                if status == "finished":
                    print("Job completed successfully!")
                    
                    # Try to get result
                    get_job_result(job_id)
                    return True
                elif status == "error":
                    print("Job failed!")
                    return False
            else:
                print(f"Error: {response.text}")
            
            # Wait before next check
            print(f"Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"Exception: {e}")
    
    print("Maximum checks reached, job may still be running")
    return None

def get_job_result(job_id):
    """Try different methods to get job results"""
    print("\n=== Trying to Get Job Results ===")
    
    # Method 1: Check container result
    print("\nMethod 1: Container Result")
    url = f"https://api.phantombuster.com/api/v2/containers/fetch"
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    params = {"id": job_id}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("resultObject")
            
            if result:
                print("Found result data!")
                print(json.dumps(result, indent=2)[:500])
                print("...")
                
                # Save to file
                with open(f"result_{job_id}.json", "w") as f:
                    json.dump(result, f, indent=2)
                print(f"Full result saved to result_{job_id}.json")
            else:
                print("No result data found")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Method 2: Try to get agent result
    print("\nMethod 2: Agent Result")
    url = f"https://api.phantombuster.com/api/v2/agents/fetch-output"
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    params = {"id": PHANTOM_AGENT_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                print("Found agent output data!")
                print(json.dumps(data, indent=2)[:500])
                print("...")
                
                # Save to file
                with open(f"agent_output_{PHANTOM_AGENT_ID}.json", "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Full output saved to agent_output_{PHANTOM_AGENT_ID}.json")
            else:
                print("No agent output data found")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def check_sheet_data():
    """Check if there's data in the Google Sheet"""
    print("\n=== Checking Google Sheet Data ===")
    print(f"Sheet URL: {SHEET_URL}")
    print("Please check the Google Sheet manually to see if data has been added.")

if __name__ == "__main__":
    print("=== PhantomBuster API Debug Script ===")
    print(f"API Key: {PHANTOM_API_KEY[:5]}...{PHANTOM_API_KEY[-5:]}")
    print(f"Agent ID: {PHANTOM_AGENT_ID}")
    print(f"Sheet ID: {SHEET_ID}")
    print(f"Sheet URL: {SHEET_URL}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get agent info and configuration
    agent_config = get_agent_info()
    
    # Try different launch methods
    print("\nWe'll try 3 different methods to launch the PhantomBuster job.")
    method = input("Which method to try? (1, 2, 3, or 'all'): ").strip().lower()
    
    job_id = None
    
    if method == '1' or method == 'all':
        job_id = try_launch_method_1()
        
    if (method == '2' or method == 'all') and not job_id:
        job_id = try_launch_method_2(agent_config)
        
    if (method == '3' or method == 'all') and not job_id:
        job_id = try_launch_method_3()
    
    if job_id:
        print(f"\n✅ Successfully launched job with ID: {job_id}")
        
        # Ask if we should monitor the job
        monitor = input("Monitor job status? (y/n): ").strip().lower()
        if monitor == 'y':
            check_job_status(job_id)
            check_sheet_data()
    else:
        print("\n❌ Failed to launch job with any method.")
        
    print("\n=== Debug Complete ===")

"""
Test script to check the new PhantomBuster agent
"""
import requests
import json
import time

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "686901552340687"  # New agent ID
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"

def test_get_agent_info():
    """Test getting agent info"""
    print("\n=== Testing Get Agent Info ===")
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
            print(f"Agent status: {data.get('status')}")
            print("\nFull response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_launch_job():
    """Test launching a job"""
    print("\n=== Testing Launch Job ===")
    url = "https://api.phantombuster.com/api/v2/agents/launch"
    
    # Try different payload formats
    payloads = [
        # Format 1: Profile scraper with spreadsheet URL
        {
            "id": PHANTOM_AGENT_ID,
            "argument": {
                "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
                "columnName": "linkedin_url",
                "numberOfProfiles": 2
            }
        },
        # Format 2: Simple launch
        {
            "id": PHANTOM_AGENT_ID
        }
    ]
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY,
        "Content-Type": "application/json"
    }
    
    job_id = None
    
    for i, payload in enumerate(payloads):
        try:
            print(f"\nTrying payload format {i+1}:")
            print(json.dumps(payload, indent=2))
            
            response = requests.post(url, json=payload, headers=headers)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("containerId")
                print(f"Success! Job ID: {job_id}")
                print(f"Full response: {json.dumps(data, indent=2)}")
                break
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")
    
    return job_id

if __name__ == "__main__":
    print("=== PhantomBuster New Agent Test ===")
    print(f"API Key: {PHANTOM_API_KEY[:5]}...{PHANTOM_API_KEY[-5:]}")
    print(f"Agent ID: {PHANTOM_AGENT_ID}")
    print(f"Sheet ID: {SHEET_ID}")
    
    # Test agent info
    test_get_agent_info()
    
    # Ask if user wants to launch a job
    response = input("\nDo you want to launch a job with the new agent? (y/n): ")
    if response.lower() == 'y':
        # Test launching a job
        job_id = test_launch_job()
        if job_id:
            print(f"\nJob launched successfully with ID: {job_id}")
            print("Check your PhantomBuster account for results.")
    else:
        print("Job launch skipped.")
    
    print("\n=== Test Complete ===")

"""
Test script to check PhantomBuster API responses
"""
import requests
import json
import time

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "3192622034872375"
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
            print(f"Agent status: {data.get('status')}")
            print(f"Agent type: {data.get('scriptName')}")
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
        },
        # Format 3: With search query
        {
            "id": PHANTOM_AGENT_ID,
            "argument": {
                "spreadsheetId": SHEET_ID,
                "numberOfProfiles": 2,
                "searchQuery": "data scientist chile"
            }
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

def test_job_status(job_id):
    """Test checking job status"""
    print("\n=== Testing Job Status ===")
    if not job_id:
        print("No job ID provided")
        return False
    
    url = f"https://api.phantombuster.com/api/v2/containers/fetch-output"
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    params = {"id": job_id}
    
    max_checks = 5
    for i in range(max_checks):
        try:
            print(f"\nCheck {i+1}/{max_checks}:")
            response = requests.get(url, params=params, headers=headers)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                print(f"Job status: {status}")
                
                # Check for output data
                output = data.get("output")
                if output:
                    print("\nOutput data found:")
                    print(json.dumps(output[:500], indent=2))  # Show first 500 chars
                else:
                    print("No output data yet")
                
                # Check for different status types
                if status == "finished":
                    print("Job completed!")
                    return True
                elif status == "error":
                    print("Job failed!")
                    return False
            else:
                print(f"Error: {response.text}")
            
            # Wait before next check
            print("Waiting 5 seconds before next check...")
            time.sleep(5)
            
        except Exception as e:
            print(f"Exception: {e}")
    
    print("Maximum checks reached, job may still be running")
    return None

def test_get_container_info(job_id):
    """Test getting container info"""
    print("\n=== Testing Get Container Info ===")
    if not job_id:
        print("No job ID provided")
        return False
    
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
            print(f"Container status: {data.get('status')}")
            print(f"Start time: {data.get('startTime')}")
            print(f"End time: {data.get('endTime')}")
            
            # Check for result data
            result = data.get("resultObject")
            if result:
                print("\nResult data found:")
                print(json.dumps(result, indent=2))
            else:
                print("No result data")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    print("=== PhantomBuster API Test ===")
    print(f"API Key: {PHANTOM_API_KEY[:5]}...{PHANTOM_API_KEY[-5:]}")
    print(f"Agent ID: {PHANTOM_AGENT_ID}")
    print(f"Sheet ID: {SHEET_ID}")
    
    # Test agent info
    test_get_agent_info()
    
    # Test launching a job
    job_id = test_launch_job()
    
    if job_id:
        # Test job status
        test_job_status(job_id)
        
        # Test container info
        test_get_container_info(job_id)
    
    print("\n=== Test Complete ===")

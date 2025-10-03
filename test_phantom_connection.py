"""
Test PhantomBuster API connection
"""
import requests
import json

def test_phantom_connection():
    """Test PhantomBuster API connection"""
    PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
    PHANTOM_AGENT_ID = "3192622034872375"
    
    print(f"Testing PhantomBuster connection with Agent ID: {PHANTOM_AGENT_ID}")
    
    # Test 1: Get agent info
    try:
        print("\n1. Testing agent info...")
        url = "https://api.phantombuster.com/api/v2/agents/fetch"
        
        headers = {
            "X-Phantombuster-Key": PHANTOM_API_KEY
        }
        
        params = {"id": PHANTOM_AGENT_ID}
        response = requests.get(url, params=params, headers=headers)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Agent name: {data.get('name', 'N/A')}")
            print(f"Agent status: {data.get('status', 'N/A')}")
            print("Agent info test: SUCCESS")
        else:
            print(f"Error: {response.text}")
            print("Agent info test: FAILED")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Agent info test: FAILED")
    
    # Test 2: Launch job
    try:
        print("\n2. Testing job launch...")
        url = "https://api.phantombuster.com/api/v2/agents/launch"
        
        # Payload for PhantomBuster
        payload = {
            "id": PHANTOM_AGENT_ID,
            "argument": {
                "searchQuery": "Chile AND finanzas",
                "numberOfProfiles": 2
            }
        }
        
        headers = {
            "X-Phantombuster-Key": PHANTOM_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("containerId")
            print(f"Job ID: {job_id}")
            print("Job launch test: SUCCESS")
            
            # Test 3: Check job status
            print("\n3. Testing job status...")
            url = f"https://api.phantombuster.com/api/v2/containers/fetch-output"
            
            params = {"id": job_id}
            response = requests.get(url, params=params, headers=headers)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                print(f"Job status: {status}")
                print("Job status test: SUCCESS")
            else:
                print(f"Error: {response.text}")
                print("Job status test: FAILED")
        else:
            print(f"Error: {response.text}")
            print("Job launch test: FAILED")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Job launch test: FAILED")
    
if __name__ == "__main__":
    test_phantom_connection()

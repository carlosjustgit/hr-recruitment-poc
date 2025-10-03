"""
Check status of a specific PhantomBuster job
"""
import requests
import json

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
JOB_ID = "6718399879282551"  # Job ID from previous test

def check_job_status():
    """Check job status"""
    print(f"Checking status for job: {JOB_ID}")
    
    url = f"https://api.phantombuster.com/api/v2/containers/fetch-output"
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    params = {"id": JOB_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print(f"Job status: {status}")
            
            # Check for output data
            output = data.get("output")
            if output:
                print("\nOutput data (first 1000 chars):")
                print(output[:1000])
                print("\n...")
            else:
                print("No output data")
            
            # Check for result data
            result = data.get("resultObject")
            if result:
                print("\nResult data:")
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

def get_container_info():
    """Get container info"""
    print(f"\nGetting container info for job: {JOB_ID}")
    
    url = f"https://api.phantombuster.com/api/v2/containers/fetch"
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    params = {"id": JOB_ID}
    
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
                print("\nResult data:")
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
    check_job_status()
    get_container_info()

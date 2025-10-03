"""
Check detailed information about a PhantomBuster job
"""
import requests
import json
import sys

# Configure output encoding to handle special characters
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
JOB_ID = "6718399879282551"  # Job ID from previous test

def check_job_output():
    """Check job output with proper encoding handling"""
    print(f"Checking output for job: {JOB_ID}")
    
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
                try:
                    print("\nOutput data (first 500 chars with encoding handling):")
                    # Handle encoding issues by replacing problematic characters
                    safe_output = output[:500].encode('utf-8', 'backslashreplace').decode('utf-8')
                    print(safe_output)
                    print("...")
                except Exception as e:
                    print(f"Error displaying output: {e}")
            else:
                print("No output data")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def check_agent_results():
    """Check agent results (which might contain the actual data)"""
    print(f"\nChecking agent results for agent: {PHANTOM_AGENT_ID}")
    
    url = f"https://api.phantombuster.com/api/v2/agents/fetch-result"
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    params = {"id": PHANTOM_AGENT_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Save the full result to a file for inspection
                with open('agent_results.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print("Full results saved to agent_results.json")
                
                # Print a summary
                if isinstance(data, list) and len(data) > 0:
                    print(f"\nFound {len(data)} results")
                    if len(data) > 0:
                        print("\nFirst result sample:")
                        print(json.dumps(data[0], indent=2, ensure_ascii=False))
                else:
                    print("No results found or unexpected format")
                
                return True
            except Exception as e:
                print(f"Error processing response: {e}")
                return False
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

# Add the agent ID
PHANTOM_AGENT_ID = "3192622034872375"

if __name__ == "__main__":
    check_job_output()
    check_agent_results()

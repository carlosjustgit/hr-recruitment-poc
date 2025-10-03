"""
Check PhantomBuster agent output
"""
import requests
import json
import sys

# Configure output encoding to handle special characters
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "3192622034872375"

def check_agent_output():
    """Check agent output"""
    print(f"Checking output for agent: {PHANTOM_AGENT_ID}")
    
    url = f"https://api.phantombuster.com/api/v2/agents/output"
    
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
                
                # Save the full output to a file for inspection
                with open('agent_output.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print("Full output saved to agent_output.json")
                
                # Print a summary
                print("\nOutput summary:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                print("...")
                
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

def check_all_available_endpoints():
    """Try various endpoints to see what works"""
    print("\nTrying various endpoints to find data:")
    
    endpoints = [
        {"name": "Agent info", "url": "https://api.phantombuster.com/api/v2/agents/fetch", "params": {"id": PHANTOM_AGENT_ID}},
        {"name": "Agent output", "url": "https://api.phantombuster.com/api/v2/agents/output", "params": {"id": PHANTOM_AGENT_ID}},
        {"name": "Agent CSV", "url": "https://api.phantombuster.com/api/v2/agents/fetch-csv", "params": {"id": PHANTOM_AGENT_ID}},
        {"name": "Agent JSON", "url": "https://api.phantombuster.com/api/v2/agents/fetch-json", "params": {"id": PHANTOM_AGENT_ID}},
        {"name": "Agent status", "url": "https://api.phantombuster.com/api/v2/agents/fetch-status", "params": {"id": PHANTOM_AGENT_ID}}
    ]
    
    headers = {
        "X-Phantombuster-Key": PHANTOM_API_KEY
    }
    
    for endpoint in endpoints:
        try:
            print(f"\nTrying {endpoint['name']} endpoint: {endpoint['url']}")
            response = requests.get(endpoint['url'], params=endpoint['params'], headers=headers)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Success! First 200 chars of response:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:200])
                    print("...")
                    
                    # Save successful responses to files
                    filename = f"{endpoint['name'].lower().replace(' ', '_')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"Full response saved to {filename}")
                    
                except Exception as e:
                    print(f"Error processing response: {e}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    check_agent_output()
    check_all_available_endpoints()

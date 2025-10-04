import requests
import json

# API configuration
api_key = '1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY'
agent_id = '686901552340687'

print("=" * 80)
print("DEBUGGING PHANTOMBUSTER DATA RETRIEVAL")
print("=" * 80)

# Step 1: Get agent output
print("\n1. Fetching agent output...")
url = "https://api.phantombuster.com/api/v2/agents/fetch-output"
headers = {"X-Phantombuster-Key": api_key}
params = {"id": agent_id}

response = requests.get(url, params=params, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    agent_output = response.json()
    print(f"Agent status: {agent_output.get('status')}")
    print(f"Is agent running: {agent_output.get('isAgentRunning')}")
    print(f"Container ID: {agent_output.get('containerId')}")
    
    # Check output for result file URLs
    output_text = agent_output.get('output', '')
    if 'result.json' in output_text or 'result.csv' in output_text:
        print("\n✓ PhantomBuster saved results!")
        
        # Extract URLs from output
        lines = output_text.split('\n')
        for line in lines:
            if 'https://' in line and ('result.json' in line or 'result.csv' in line):
                print(f"  Found: {line.strip()}")
    else:
        print("\n✗ No result files found in output")

# Step 2: Try to get the actual data
print("\n2. Fetching result data from agent output endpoint...")
result_url = f"https://api.phantombuster.com/api/v1/agent/{agent_id}/output"
result_response = requests.get(result_url, headers=headers)
print(f"Status: {result_response.status_code}")

if result_response.status_code == 200:
    try:
        result_data = result_response.json()
        print(f"Response type: {type(result_data)}")
        
        if isinstance(result_data, dict):
            print(f"Response keys: {list(result_data.keys())}")
            
            # Check for 'data' key
            if 'data' in result_data:
                data = result_data['data']
                print(f"\n✓ Found 'data' key!")
                print(f"Data type: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"Data is a dict with keys: {list(data.keys())}")
                    
                    # Check for common result keys
                    for key in ['resultObject', 'results', 'output', 'items']:
                        if key in data:
                            print(f"\n  Found '{key}' in data:")
                            print(f"  Type: {type(data[key])}")
                            if isinstance(data[key], list):
                                print(f"  Length: {len(data[key])}")
                                if len(data[key]) > 0:
                                    print(f"  First item keys: {list(data[key][0].keys())[:10] if isinstance(data[key][0], dict) else 'Not a dict'}")
                            elif isinstance(data[key], dict):
                                print(f"  Keys: {list(data[key].keys())[:10]}")
                
                elif isinstance(data, list):
                    print(f"Data is a list with {len(data)} items")
                    if len(data) > 0:
                        print(f"First item type: {type(data[0])}")
                        if isinstance(data[0], dict):
                            print(f"First item keys: {list(data[0].keys())[:10]}")
                            print(f"\nFirst item sample:")
                            print(json.dumps(data[0], indent=2)[:500])
                else:
                    print(f"Data value: {data}")
            else:
                print(f"\n✗ No 'data' key found in response")
                print(f"Full response structure:")
                print(json.dumps(result_data, indent=2)[:1000])
        
        elif isinstance(result_data, list):
            print(f"Response is a list with {len(result_data)} items")
            if len(result_data) > 0:
                print(f"First item type: {type(result_data[0])}")
                if isinstance(result_data[0], dict):
                    print(f"First item keys: {list(result_data[0].keys())[:10]}")
        
    except json.JSONDecodeError:
        print("Failed to parse as JSON")
        print(f"Response text (first 500 chars): {result_response.text[:500]}")

# Step 3: Try to fetch the result files directly if URLs were found
print("\n3. Looking for result file URLs in the output...")
if response.status_code == 200:
    agent_output = response.json()
    output_text = agent_output.get('output', '')
    
    # Try to extract JSON result URL
    for line in output_text.split('\n'):
        if 'result.json' in line and 'https://' in line:
            # Extract URL
            import re
            url_match = re.search(r'https://[^\s]+result\.json', line)
            if url_match:
                json_url = url_match.group(0)
                print(f"\nFound result JSON URL: {json_url}")
                print("Fetching data from this URL...")
                
                json_response = requests.get(json_url)
                if json_response.status_code == 200:
                    try:
                        json_data = json_response.json()
                        print(f"✓ Successfully fetched JSON data!")
                        print(f"Data type: {type(json_data)}")
                        if isinstance(json_data, list):
                            print(f"Number of records: {len(json_data)}")
                            if len(json_data) > 0:
                                print(f"First record keys: {list(json_data[0].keys())[:10]}")
                                print(f"\nFirst record sample:")
                                print(json.dumps(json_data[0], indent=2)[:800])
                        elif isinstance(json_data, dict):
                            print(f"Data keys: {list(json_data.keys())}")
                    except:
                        print("Failed to parse JSON from URL")
                else:
                    print(f"Failed to fetch JSON: {json_response.status_code}")
                break

print("\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)

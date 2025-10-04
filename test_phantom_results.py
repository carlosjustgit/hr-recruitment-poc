import requests
import json

# API configuration
api_key = '1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY'
agent_id = '686901552340687'

# Test fetch-output endpoint
def test_fetch_output():
    url = 'https://api.phantombuster.com/api/v2/agents/fetch-output'
    headers = {'Accept': 'application/json', 'X-Phantombuster-Key': api_key}
    params = {'id': agent_id}
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Fetch-output status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Output type: {type(data)}")
        print(f"Output contains: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        print(f"Container ID: {data.get('containerId', 'Not found')}")
        print(f"Status: {data.get('status', 'Not found')}")
        print(f"Is agent running: {data.get('isAgentRunning', 'Not found')}")
        print("---")
    else:
        print(f"Error: {response.text}")

# Test fetch-result endpoint
def test_fetch_result():
    url = 'https://api.phantombuster.com/api/v2/agents/fetch-result'
    headers = {'Accept': 'application/json', 'X-Phantombuster-Key': api_key}
    params = {'id': agent_id}
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Fetch-result status code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Result type: {type(data)}")
            if isinstance(data, list):
                print(f"Number of records: {len(data)}")
                if len(data) > 0:
                    print(f"First record keys: {list(data[0].keys())[:10]}")
                    print(f"Sample data: {json.dumps(data[0], indent=2)[:500]}...")
            else:
                print(f"Result data: {data}")
        except json.JSONDecodeError:
            print("Could not decode JSON response")
            print(f"Response text: {response.text[:200]}...")
    else:
        print(f"Error: {response.text}")

# Test fetch-json-result endpoint
def test_fetch_json_result():
    url = 'https://api.phantombuster.com/api/v2/agents/fetch-json-result'
    headers = {'Accept': 'application/json', 'X-Phantombuster-Key': api_key}
    params = {'id': agent_id}
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Fetch-json-result status code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"JSON Result type: {type(data)}")
            if isinstance(data, list):
                print(f"Number of records: {len(data)}")
                if len(data) > 0:
                    print(f"First record keys: {list(data[0].keys())[:10]}")
                    print(f"Sample data: {json.dumps(data[0], indent=2)[:500]}...")
            else:
                print(f"JSON Result data: {data}")
        except json.JSONDecodeError:
            print("Could not decode JSON response")
            print(f"Response text: {response.text[:200]}...")
    else:
        print(f"Error: {response.text}")

# Test agent output endpoint
def test_agent_output():
    url = f'https://api.phantombuster.com/api/v1/agent/{agent_id}/output'
    headers = {'Accept': 'application/json', 'X-Phantombuster-Key': api_key}
    
    response = requests.get(url, headers=headers)
    print(f"Agent output status code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Agent output type: {type(data)}")
            print(f"Agent output keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict) and 'data' in data:
                print(f"Data sample: {json.dumps(data['data'], indent=2)[:500]}...")
        except json.JSONDecodeError:
            print("Could not decode JSON response")
            print(f"Response text: {response.text[:200]}...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("=== Testing PhantomBuster API Integration ===")
    print("\n1. Testing fetch-output endpoint:")
    test_fetch_output()
    
    print("\n2. Testing fetch-result endpoint:")
    test_fetch_result()
    
    print("\n3. Testing fetch-json-result endpoint:")
    test_fetch_json_result()
    
    print("\n4. Testing agent output endpoint:")
    test_agent_output()
    
    print("\n=== Test complete ===")

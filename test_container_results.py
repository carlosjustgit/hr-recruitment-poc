import requests
import json

# API configuration
api_key = '1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY'
container_id = '217246259434494'  # From the previous test output

# Test container output endpoint
def test_container_output():
    url = f'https://api.phantombuster.com/api/v2/containers/{container_id}/output'
    headers = {'Accept': 'application/json', 'X-Phantombuster-Key': api_key}
    
    response = requests.get(url, headers=headers)
    print(f"Container output status code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Container output type: {type(data)}")
            print(f"Container output keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            print(f"Output sample: {data.get('output', 'Not found')[:200]}...")
        except json.JSONDecodeError:
            print("Could not decode JSON response")
            print(f"Response text: {response.text[:200]}...")
    else:
        print(f"Error: {response.text}")

# Test container result endpoint
def test_container_result():
    url = f'https://api.phantombuster.com/api/v2/containers/{container_id}/result'
    headers = {'Accept': 'application/json', 'X-Phantombuster-Key': api_key}
    
    response = requests.get(url, headers=headers)
    print(f"Container result status code: {response.status_code}")
    
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

if __name__ == "__main__":
    print("=== Testing PhantomBuster Container API ===")
    print("\n1. Testing container output endpoint:")
    test_container_output()
    
    print("\n2. Testing container result endpoint:")
    test_container_result()
    
    print("\n=== Test complete ===")

"""
Check PhantomBuster Agent Configuration

This script will:
1. Get the current configuration of the LinkedIn Profile Scraper agent
2. Print the configuration details
"""
import requests
import json

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "686901552340687"  # LinkedIn Profile Scraper

def get_agent_info():
    """Get agent information"""
    url = "https://api.phantombuster.com/api/v2/agents/fetch"
    headers = {"X-Phantombuster-Key": PHANTOM_API_KEY}
    params = {"id": PHANTOM_AGENT_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def get_agent_config():
    """Get the agent's current configuration"""
    agent_info = get_agent_info()
    
    if "error" in agent_info:
        print(f"Error getting agent info: {agent_info['error']}")
        return None
    
    try:
        # Extract and parse the argument JSON
        argument_str = agent_info.get('argument', '{}')
        config = json.loads(argument_str)
        return config
    except Exception as e:
        print(f"Error parsing agent config: {e}")
        return None

def main():
    """Main function"""
    print("=== Checking PhantomBuster Agent Configuration ===")
    
    # Get agent info
    print("\n1. Getting agent info...")
    agent_info = get_agent_info()
    
    if "error" in agent_info:
        print(f"Error getting agent info: {agent_info['error']}")
        return
    
    print(f"Agent Name: {agent_info.get('name', 'Unknown')}")
    print(f"Agent Status: {agent_info.get('status', 'Unknown')}")
    
    # Get agent config
    print("\n2. Getting agent configuration...")
    config = get_agent_config()
    
    if config:
        print("\nCurrent Configuration:")
        print(json.dumps(config, indent=2))
        
        # Check for important fields
        print("\nChecking important fields:")
        
        # Check spreadsheetUrl
        spreadsheet_url = config.get('spreadsheetUrl', '')
        print(f"Spreadsheet URL: {spreadsheet_url}")
        
        # Check columnName
        column_name = config.get('columnName', '')
        print(f"Column Name: {column_name}")
        
        # Check numberOfProfilesPerLaunch
        num_profiles = config.get('numberOfProfilesPerLaunch', config.get('numberOfProfiles', 0))
        print(f"Number of Profiles: {num_profiles}")
    else:
        print("Failed to get agent configuration")
    
    print("\n=== Check Complete ===")

if __name__ == "__main__":
    main()

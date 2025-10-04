import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Constants
DATA_ENRICHER_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
DATA_ENRICHER_AGENT_ID = "686901552340687"

def get_enricher_results():
    """Get the results of the enrichment job directly from PhantomBuster"""
    try:
        # Try the agent's fetch-output endpoint
        url = "https://api.phantombuster.com/api/v2/agents/fetch-output"
        headers = {"X-Phantombuster-Key": DATA_ENRICHER_API_KEY}
        params = {"id": DATA_ENRICHER_AGENT_ID}
        
        print("Fetching data from PhantomBuster API...")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            agent_output = response.json()
            if agent_output and "output" in agent_output:
                print("Successfully retrieved agent output")
                
                # Now get the actual result data using agent output endpoint
                result_url = f"https://api.phantombuster.com/api/v1/agent/{DATA_ENRICHER_AGENT_ID}/output"
                result_response = requests.get(result_url, headers=headers)
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if isinstance(result_data, dict) and "data" in result_data:
                        print(f"Successfully retrieved result data")
                        return result_data.get("data", {})
        
        print(f"Failed to get data: Status code {response.status_code}")
        return None
    except Exception as e:
        print(f"Exception in get_enricher_results: {e}")
        return None

def fix_data_structure(data):
    """Normalize data structure to ensure all dictionaries have the same keys"""
    if not data:
        return []
    
    # Get all unique keys across all dictionaries
    all_keys = set()
    for item in data:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    
    # Create a list of normalized dictionaries
    normalized_data = []
    for item in data:
        if isinstance(item, dict):
            # Create a new dict with all keys set to None, then update with actual values
            normalized_item = {key: None for key in all_keys}
            normalized_item.update(item)
            normalized_data.append(normalized_item)
    
    return normalized_data

def main():
    # Get data from PhantomBuster
    data = get_enricher_results()
    
    if not data:
        print("No data retrieved from PhantomBuster")
        return
    
    # Fix data structure
    normalized_data = fix_data_structure(data)
    
    # Try to create DataFrame
    try:
        df = pd.DataFrame(normalized_data)
        print(f"Successfully created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        
        # Save to CSV for inspection
        df.to_csv("normalized_data.csv", index=False)
        print("Data saved to normalized_data.csv")
        
        # Print first few rows
        print("\nFirst 2 rows:")
        print(df.head(2))
        
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        
        # Debug information
        print("\nData structure:")
        for i, item in enumerate(normalized_data[:2]):
            print(f"Item {i}:")
            print(type(item))
            if isinstance(item, dict):
                print(f"Keys: {list(item.keys())[:5]}...")
            else:
                print(f"Value: {item}")

if __name__ == "__main__":
    main()

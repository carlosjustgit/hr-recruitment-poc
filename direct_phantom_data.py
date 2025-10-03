"""
Direct PhantomBuster Data Fetcher
This script directly fetches and displays data from PhantomBuster, bypassing any issues with our app
"""
import requests
import pandas as pd
import json
import streamlit as st

# Configuration
PHANTOM_API_KEY = "1SROua2I62PpnUfCj52i0w3Dc3X50lRNZV1BFDA62LY"
PHANTOM_AGENT_ID = "686901552340687"  # LinkedIn Profile Scraper

st.set_page_config(page_title="PhantomBuster Direct Data", page_icon="🔍", layout="wide")
st.title("PhantomBuster Direct Data Viewer")
st.write("This tool directly fetches data from PhantomBuster, bypassing any issues with our app")

@st.cache_data(ttl=60)  # Cache for 1 minute
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

def get_agent_output():
    """Get agent output"""
    url = "https://api.phantombuster.com/api/v2/agents/output"
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

def get_agent_result():
    """Get agent result data"""
    # Try different endpoints to get the data
    endpoints = [
        {"name": "JSON Result", "url": "https://api.phantombuster.com/api/v2/agents/fetch-result"},
        {"name": "JSON Output", "url": "https://api.phantombuster.com/api/v2/agents/fetch-json-result"},
        {"name": "CSV Result", "url": "https://api.phantombuster.com/api/v2/agents/fetch-csv-result"}
    ]
    
    results = {}
    
    for endpoint in endpoints:
        url = endpoint["url"]
        headers = {"X-Phantombuster-Key": PHANTOM_API_KEY}
        params = {"id": PHANTOM_AGENT_ID}
        
        try:
            st.write(f"Trying endpoint: {endpoint['name']}")
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results[endpoint["name"]] = data
                    st.success(f"✅ Success with {endpoint['name']}!")
                except:
                    st.warning(f"⚠️ Got response but couldn't parse JSON from {endpoint['name']}")
                    results[endpoint["name"]] = {"raw": response.text[:1000] + "..."}
            else:
                st.error(f"❌ Error with {endpoint['name']}: {response.status_code}")
                results[endpoint["name"]] = {"error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            st.error(f"❌ Exception with {endpoint['name']}: {str(e)}")
            results[endpoint["name"]] = {"error": str(e)}
    
    return results

def get_latest_container_id():
    """Get the latest container ID"""
    url = "https://api.phantombuster.com/api/v2/containers/fetch-all"
    headers = {"X-Phantombuster-Key": PHANTOM_API_KEY}
    params = {"agentId": PHANTOM_AGENT_ID}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            containers = response.json()
            if containers and len(containers) > 0:
                # Sort by start time, descending
                containers.sort(key=lambda x: x.get("startTime", 0), reverse=True)
                return containers[0].get("id")
            else:
                return None
        else:
            st.error(f"Error getting containers: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Exception getting containers: {str(e)}")
        return None

def get_container_output(container_id):
    """Get container output"""
    url = "https://api.phantombuster.com/api/v2/containers/fetch-output"
    headers = {"X-Phantombuster-Key": PHANTOM_API_KEY}
    params = {"id": container_id}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def get_store_data():
    """Get data from PhantomBuster's store"""
    url = "https://api.phantombuster.com/api/v2/store/get"
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

# Main app
st.header("Agent Information")
agent_info = get_agent_info()

if "error" in agent_info:
    st.error(f"Error getting agent info: {agent_info['error']}")
else:
    st.write(f"Agent Name: {agent_info.get('name', 'Unknown')}")
    st.write(f"Agent Script: {agent_info.get('script', 'Unknown')}")
    
    with st.expander("Full Agent Info"):
        st.json(agent_info)

# Get latest container
st.header("Latest Container")
container_id = get_latest_container_id()

if container_id:
    st.write(f"Latest Container ID: {container_id}")
    
    container_output = get_container_output(container_id)
    with st.expander("Container Output"):
        st.json(container_output)
else:
    st.warning("No containers found")

# Get agent results
st.header("Agent Results")
if st.button("Fetch Results"):
    with st.spinner("Fetching results from PhantomBuster..."):
        results = get_agent_result()
        
        for endpoint, data in results.items():
            with st.expander(f"Results from {endpoint}"):
                if "error" in data:
                    st.error(f"Error: {data['error']}")
                elif "raw" in data:
                    st.text(data["raw"])
                elif isinstance(data, list):
                    st.write(f"Found {len(data)} records")
                    if len(data) > 0:
                        # Convert to DataFrame for better display
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                        
                        # Save as CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="phantombuster_data.csv",
                            mime="text/csv"
                        )
                else:
                    st.json(data)

# Get store data
st.header("PhantomBuster Store Data")
if st.button("Fetch Store Data"):
    with st.spinner("Fetching data from PhantomBuster store..."):
        store_data = get_store_data()
        
        if "error" in store_data:
            st.error(f"Error: {store_data['error']}")
        else:
            st.json(store_data)

# Manual CSV URL input
st.header("Direct CSV Access")
st.write("PhantomBuster often stores results as CSV files. If you have a direct URL to the CSV, enter it below:")

csv_url = st.text_input("CSV URL")
if csv_url:
    try:
        df = pd.read_csv(csv_url)
        st.success(f"Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        st.dataframe(df)
        
        # Save as CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="phantombuster_data.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")

"""
Fix LinkedIn URLs in Google Sheet

This script will:
1. Check what's currently in the Google Sheet
2. Add properly formatted LinkedIn URLs
3. Ensure the column names match exactly what PhantomBuster expects
"""
import streamlit as st
import pandas as pd
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time

# Configuration
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"

st.set_page_config(page_title="Fix LinkedIn URLs", page_icon="🔧", layout="wide")
st.title("Fix LinkedIn URLs in Google Sheet")
st.write("This tool will add properly formatted LinkedIn URLs to your Google Sheet")

# Sample LinkedIn URLs
SAMPLE_LINKEDIN_URLS = [
    {
        "Profile Url": "https://www.linkedin.com/in/alisson-frota/",
        "First Name": "Alisson",
        "Last Name": "Frota"
    },
    {
        "Profile Url": "https://www.linkedin.com/in/herbert-zapata-salvo/",
        "First Name": "Herbert",
        "Last Name": "Zapata Salvo"
    },
    {
        "Profile Url": "https://www.linkedin.com/in/rkniazev/",
        "First Name": "Roman",
        "Last Name": "K."
    },
    {
        "Profile Url": "https://www.linkedin.com/in/enbonnet/",
        "First Name": "Ender",
        "Last Name": "Bonnet"
    },
    {
        "Profile Url": "https://www.linkedin.com/in/pierinazaramella/",
        "First Name": "Pierina",
        "Last Name": "Zaramella"
    },
    {
        "Profile Url": "https://www.linkedin.com/in/carlos-justino/",
        "First Name": "Carlos",
        "Last Name": "Justino"
    },
    {
        "Profile Url": "https://www.linkedin.com/in/diego-ramirez-chile/",
        "First Name": "Diego",
        "Last Name": "Ramirez"
    },
    {
        "Profile Url": "https://www.linkedin.com/in/maria-gonzalez-marketing/",
        "First Name": "Maria",
        "Last Name": "Gonzalez"
    },
    {
        "Profile Url": "https://www.linkedin.com/in/ana-silva-dev/",
        "First Name": "Ana",
        "Last Name": "Silva"
    },
    {
        "Profile Url": "https://www.linkedin.com/in/roberto-mendez-tech/",
        "First Name": "Roberto",
        "Last Name": "Mendez"
    }
]

def get_sheet_service():
    """Get Google Sheets service"""
    try:
        # Check if credentials file exists
        if not os.path.exists("service-account-key.json"):
            st.error("Service account key file not found")
            return None
            
        # Setup credentials
        credentials = Credentials.from_service_account_file(
            "service-account-key.json",
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Error setting up Google Sheets service: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

def get_sheet_data(service, sheet_name="candidatos"):
    """Get data from Google Sheet"""
    try:
        # Get data from sheet
        sheet_range = f"{sheet_name}!A1:ZZ"
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=sheet_range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            st.warning("No data found in sheet")
            return {"headers": [], "data": []}
            
        # Convert to list of dicts
        headers = values[0]
        data = []
        
        for row in values[1:]:
            # Ensure row is same length as headers
            while len(row) < len(headers):
                row.append("")
                
            item = {}
            for i, header in enumerate(headers):
                item[header] = row[i]
                
            data.append(item)
            
        return {"headers": headers, "data": data}
        
    except Exception as e:
        st.error(f"Error loading sheet data: {e}")
        import traceback
        st.code(traceback.format_exc())
        return {"headers": [], "data": []}

def clear_sheet(service, sheet_name="candidatos"):
    """Clear all data from the spreadsheet"""
    try:
        # Clear the entire worksheet
        clear_range = f"{sheet_name}!A1:ZZ1000"  # Adjust range as needed
        result = service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range=clear_range,
            body={}
        ).execute()
        
        # Debug info
        cleared_range = result.get('clearedRange', '')
        st.info(f"✅ Successfully cleared data from {cleared_range}")
        return True
            
    except Exception as e:
        st.error(f"Error clearing sheet: {e}")
        import traceback
        st.code(traceback.format_exc())
        return False

def write_sample_data(service, sheet_name="candidatos"):
    """Write sample LinkedIn URLs to the Google Sheet"""
    try:
        # Define the headers - EXACTLY as PhantomBuster expects
        headers = ["Profile Url", "First Name", "Last Name"]
        
        # Convert sample data to rows
        rows = [headers]  # First row is headers
        for item in SAMPLE_LINKEDIN_URLS:
            row = [item.get(header, "") for header in headers]
            rows.append(row)
        
        # Write to sheet
        body = {'values': rows}
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"{sheet_name}!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        st.success(f"✅ Successfully wrote {len(rows)-1} LinkedIn URLs to sheet")
        return True
        
    except Exception as e:
        st.error(f"Error writing to sheet: {e}")
        import traceback
        st.code(traceback.format_exc())
        return False

def main():
    """Main function"""
    # Get Google Sheets service
    service = get_sheet_service()
    if not service:
        st.error("Failed to initialize Google Sheets service")
        return
    
    # Get current sheet data
    sheet_data = get_sheet_data(service)
    
    # Show current headers
    st.subheader("Current Sheet Headers")
    if sheet_data["headers"]:
        st.write(sheet_data["headers"])
    else:
        st.warning("No headers found in sheet")
    
    # Show current data
    st.subheader("Current Sheet Data")
    if sheet_data["data"]:
        df = pd.DataFrame(sheet_data["data"])
        st.dataframe(df)
    else:
        st.warning("No data found in sheet")
    
    # Check if "Profile Url" column exists
    has_profile_url = "Profile Url" in sheet_data["headers"]
    
    # Check if there are any LinkedIn URLs in the data
    linkedin_urls_count = 0
    if has_profile_url:
        for row in sheet_data["data"]:
            if "Profile Url" in row and "linkedin.com/in/" in str(row["Profile Url"]).lower():
                linkedin_urls_count += 1
    
    st.info(f"Found {linkedin_urls_count} valid LinkedIn URLs in the sheet")
    
    # Actions
    st.subheader("Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Sheet"):
            with st.spinner("Clearing sheet..."):
                success = clear_sheet(service)
                if success:
                    st.success("Sheet cleared successfully")
                    time.sleep(1)
                    st.rerun()
    
    with col2:
        if st.button("Add Sample LinkedIn URLs"):
            with st.spinner("Adding sample LinkedIn URLs..."):
                success = write_sample_data(service)
                if success:
                    st.success("Sample LinkedIn URLs added successfully")
                    time.sleep(1)
                    st.rerun()
    
    # All-in-one button
    if st.button("🔄 Fix Everything (Clear + Add Sample URLs)", type="primary"):
        with st.spinner("Fixing everything..."):
            # Clear sheet
            st.write("Step 1: Clearing sheet...")
            clear_success = clear_sheet(service)
            if not clear_success:
                st.error("Failed to clear sheet")
                return
            
            # Add sample data
            st.write("Step 2: Adding sample LinkedIn URLs...")
            data_success = write_sample_data(service)
            if not data_success:
                st.error("Failed to add sample LinkedIn URLs")
                return
            
            st.success("✅ Everything fixed successfully!")
            st.balloons()
            time.sleep(2)
            st.rerun()
    
    # Google Sheet link
    st.subheader("Google Sheet")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
    st.markdown(f"[Open Google Sheet]({sheet_url})")

if __name__ == "__main__":
    main()

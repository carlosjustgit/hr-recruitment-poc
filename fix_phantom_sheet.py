"""
Script to fix the Google Sheet format for PhantomBuster
"""
import os
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configuration
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"

def main():
    st.title("Fix Google Sheet for PhantomBuster")
    
    # Setup credentials
    if not os.path.exists("service-account-key.json"):
        st.error("Service account key file not found")
        return
        
    credentials = Credentials.from_service_account_file(
        "service-account-key.json",
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=credentials)
    
    # Sample LinkedIn URLs
    sample_data = [
        {
            "Profile Url": "https://www.linkedin.com/in/franciscocj/",
        },
        {
            "Profile Url": "https://www.linkedin.com/in/karla-sg/",
        },
        {
            "Profile Url": "https://www.linkedin.com/in/nicol%C3%A1s-caroca-pinto-571a43218/",
        },
        {
            "Profile Url": "https://www.linkedin.com/in/christopher-georgi-93a787163/",
        },
        {
            "Profile Url": "https://www.linkedin.com/in/robertcontardo/",
        }
    ]
    
    if st.button("Fix Sheet Format", type="primary"):
        with st.spinner("Fixing Google Sheet format..."):
            # Clear the sheet
            try:
                clear_range = "candidatos!A1:ZZ1000"
                service.spreadsheets().values().clear(
                    spreadsheetId=SHEET_ID,
                    range=clear_range,
                    body={}
                ).execute()
                st.success("Cleared sheet")
            except Exception as e:
                st.error(f"Error clearing sheet: {e}")
                return
            
            # Write only the "Profile Url" column - exactly what PhantomBuster expects
            values = [["Profile Url"]]  # Header row with EXACT column name
            
            for row in sample_data:
                values.append([row["Profile Url"]])
            
            try:
                body = {'values': values}
                result = service.spreadsheets().values().update(
                    spreadsheetId=SHEET_ID,
                    range="candidatos!A1",
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                st.success(f"✅ Sheet fixed! Updated {result.get('updatedRows')} rows.")
                st.info("The sheet now has exactly the format PhantomBuster expects.")
                
                # Show the data
                df = pd.DataFrame(sample_data)
                st.dataframe(df)
                
            except Exception as e:
                st.error(f"Error writing to sheet: {e}")
                return

if __name__ == "__main__":
    main()

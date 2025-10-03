"""
Direct Google Sheet Data Access
This script directly reads data from the Google Sheet and displays it
"""
import streamlit as st
import pandas as pd
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configuration
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"

st.set_page_config(page_title="Google Sheet Direct Data", page_icon="📊", layout="wide")
st.title("Google Sheet Direct Data Viewer")
st.write("This tool directly reads data from the Google Sheet, bypassing any issues with our app")

# Function to get sheet data
def get_sheet_data():
    """Get data directly from Google Sheet"""
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
        
        # Get sheet names
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_names = [sheet.get("properties", {}).get("title") for sheet in sheets]
        
        st.success(f"Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
        
        # Get data from selected sheet
        selected_sheet = st.selectbox("Select Sheet", sheet_names)
        
        if selected_sheet:
            # Get all data from the sheet
            sheet_range = f"{selected_sheet}!A1:ZZ"
            result = service.spreadsheets().values().get(
                spreadsheetId=SHEET_ID,
                range=sheet_range
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                st.warning(f"No data found in sheet '{selected_sheet}'")
                return None
                
            # Convert to DataFrame
            headers = values[0]
            data = values[1:] if len(values) > 1 else []
            
            # Ensure all rows have the same length as headers
            for i in range(len(data)):
                while len(data[i]) < len(headers):
                    data[i].append("")
            
            df = pd.DataFrame(data, columns=headers)
            
            # Display data
            st.success(f"Loaded {len(df)} rows and {len(df.columns)} columns from sheet '{selected_sheet}'")
            
            # Filter columns
            all_columns = list(df.columns)
            selected_columns = st.multiselect("Select columns to display", all_columns, default=all_columns[:10])
            
            if selected_columns:
                st.dataframe(df[selected_columns])
            else:
                st.dataframe(df)
            
            # Download as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{selected_sheet}_data.csv",
                mime="text/csv"
            )
            
            return df
            
    except Exception as e:
        st.error(f"Error loading sheet data: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

# Direct URL access
st.header("Google Sheet Direct Access")
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
st.markdown(f"[Open Google Sheet in Browser]({sheet_url})")

# Get data
st.header("Sheet Data")
df = get_sheet_data()

# Data analysis
if df is not None and not df.empty:
    st.header("Data Analysis")
    
    # Show column stats
    st.subheader("Column Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Column counts (non-empty values):")
        counts = df.count()
        st.bar_chart(counts)
    
    with col2:
        # Check for LinkedIn URLs
        if 'profileUrl' in df.columns:
            linkedin_urls = df['profileUrl'].str.contains('linkedin.com', na=False).sum()
            st.metric("LinkedIn URLs", linkedin_urls)
        
        # Check for errors
        if 'error' in df.columns:
            errors = df['error'].notna().sum()
            st.metric("Errors", errors)
    
    # Show sample rows with LinkedIn data
    st.subheader("Sample Rows with LinkedIn Data")
    if 'profileUrl' in df.columns:
        linkedin_rows = df[df['profileUrl'].str.contains('linkedin.com', na=False)]
        if not linkedin_rows.empty:
            st.dataframe(linkedin_rows.head(5))
        else:
            st.warning("No rows with LinkedIn URLs found")
    
    # Show sample rows with errors
    st.subheader("Sample Rows with Errors")
    if 'error' in df.columns:
        error_rows = df[df['error'].notna()]
        if not error_rows.empty:
            st.dataframe(error_rows.head(5))
        else:
            st.success("No rows with errors found")

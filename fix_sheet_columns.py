"""
Fix Google Sheet Columns

This script will:
1. Read the current data from the Google Sheet
2. Update the column headers to match PhantomBuster's expected format
3. Add sample data with correct column structure
"""
import os
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time

# Configuration
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"

st.set_page_config(page_title="Fix Google Sheet Columns", page_icon="🔧", layout="wide")
st.title("Fix Google Sheet Columns")
st.write("This tool will fix the column headers in your Google Sheet to match PhantomBuster's expected format")

# Define the expected column headers for PhantomBuster LinkedIn Profile Scraper
EXPECTED_HEADERS = [
    "Profile Url", "Error", "Refreshed At", "Scraper Profile Id", "Scraper Full Name",
    "Company Industry", "Company Name", "Company Website", "First Name", "Last Name",
    "Linkedin Company Url", "Linkedin Company Slug", "Linkedin Company Id", "Linkedin Description",
    "Linkedin Headline", "Linkedin Is Hiring Badge", "Linkedin Is Open To Work Badge",
    "Linkedin Job Date Range", "Linkedin Job Description", "Linkedin Job Location",
    "Linkedin Job Title", "Linkedin Previous Company Slug", "Linkedin Previous Job Date Range",
    "Linkedin Previous Job Location", "Linkedin Previous Job Title", "Linkedin Profile Id",
    "Linkedin Profile Slug", "Linkedin Profile Url", "Linkedin Profile Urn",
    "Linkedin Profile Image Urn", "Linkedin Profile Image Url", "Linkedin School Date Range",
    "Linkedin School Degree", "Linkedin Skills Label", "Location", "Previous Company Name",
    "Professional Email", "Mutual Connections Url", "Connections Url", "Linkedin Company Name",
    "Linkedin Company Description", "Linkedin Company Tagline", "Linkedin Company Follower Count",
    "Linkedin Company Website", "Linkedin Company Employees Count", "Linkedin Company Size",
    "Linkedin Company Headquarter", "Linkedin Company Industry", "Linkedin Company Founded",
    "Linkedin Company Specialities", "Linkedin School Description", "Linkedin School Url",
    "Linkedin School Company Slug", "Linkedin School Name", "Linkedin Previous School Url",
    "Linkedin Previous School Company Slug", "Linkedin Previous School Date Range",
    "Linkedin Previous School Degree", "Linkedin Previous School Name", "Linkedin Previous Job Description"
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
            return []
            
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

def update_sheet_headers(service, sheet_name="candidatos"):
    """Update sheet headers to match PhantomBuster's expected format"""
    try:
        # Write headers
        body = {'values': [EXPECTED_HEADERS]}
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"{sheet_name}!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        st.success("✅ Successfully updated sheet headers")
        return True
        
    except Exception as e:
        st.error(f"Error updating sheet headers: {e}")
        import traceback
        st.code(traceback.format_exc())
        return False

def add_sample_data(service, sheet_name="candidatos"):
    """Add sample data with correct column structure"""
    try:
        # Sample data
        sample_data = [
            {
                "Profile Url": "https://www.linkedin.com/in/alisson-frota/",
                "First Name": "Alisson",
                "Last Name": "Frota Soares",
                "Linkedin Headline": "Developer Accenture Portugal expertise in PHP and Web",
                "Location": "Chile",
                "Company Name": "Accenture Portugal",
                "Company Industry": "Information Technology & Services",
                "Linkedin Job Title": "Desenvolvedor",
                "Linkedin Job Date Range": "Sep 2024 - Present",
                "Linkedin School Degree": "Gestão e programação de sistemas informáticos",
                "Linkedin School Date Range": "Sep 2018 - Jun 2021",
                "Linkedin Skills Label": "Tailwind CSS, Python, Django, PHP, Laravel, Desenvolvimento web"
            },
            {
                "Profile Url": "https://www.linkedin.com/in/herbert-zapata-salvo/",
                "First Name": "Herbert",
                "Last Name": "Zapata Salvo",
                "Linkedin Headline": "Full Stack Developer",
                "Location": "Santiago",
                "Company Name": "Tech Company Chile",
                "Company Industry": "Software Development",
                "Linkedin Job Title": "Full Stack Developer",
                "Linkedin Job Date Range": "Jan 2023 - Present",
                "Linkedin School Degree": "Computer Science",
                "Linkedin School Date Range": "2018 - 2022",
                "Linkedin Skills Label": "JavaScript, React, Node.js, MongoDB, Express"
            },
            {
                "Profile Url": "https://www.linkedin.com/in/rkniazev/",
                "First Name": "Roman",
                "Last Name": "K.",
                "Linkedin Headline": "Kotlin (java) developer",
                "Location": "Chile",
                "Company Name": "Tech Company",
                "Company Industry": "Software Development",
                "Linkedin Job Title": "Kotlin Developer",
                "Linkedin Job Date Range": "Mar 2022 - Present",
                "Linkedin School Degree": "Computer Science",
                "Linkedin School Date Range": "2015 - 2019",
                "Linkedin Skills Label": "Kotlin, Java, Android, Spring Boot, SQL"
            },
            {
                "Profile Url": "https://www.linkedin.com/in/enbonnet/",
                "First Name": "Ender",
                "Last Name": "Bonnet",
                "Linkedin Headline": "Frontend Developer at Lilo",
                "Location": "Chile",
                "Company Name": "Lilo",
                "Company Industry": "Web Development",
                "Linkedin Job Title": "Frontend Developer",
                "Linkedin Job Date Range": "Jan 2023 - Present",
                "Linkedin School Degree": "Web Development",
                "Linkedin School Date Range": "2017 - 2020",
                "Linkedin Skills Label": "JavaScript, React, Vue.js, CSS, HTML"
            },
            {
                "Profile Url": "https://www.linkedin.com/in/pierinazaramella/",
                "First Name": "Pierina",
                "Last Name": "Zaramella",
                "Linkedin Headline": "FullStack Developer en Walmart Chile",
                "Location": "Santiago",
                "Company Name": "Walmart Chile",
                "Company Industry": "Retail",
                "Linkedin Job Title": "FullStack Developer",
                "Linkedin Job Date Range": "Jun 2022 - Present",
                "Linkedin School Degree": "Computer Science",
                "Linkedin School Date Range": "2016 - 2020",
                "Linkedin Skills Label": "JavaScript, Python, React, Django, PostgreSQL"
            }
        ]
        
        # Convert to rows
        rows = []
        for item in sample_data:
            row = []
            for header in EXPECTED_HEADERS:
                row.append(item.get(header, ""))
            rows.append(row)
        
        # Write data
        body = {'values': rows}
        service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=f"{sheet_name}!A2",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        st.success(f"✅ Successfully added {len(rows)} sample rows")
        return True
        
    except Exception as e:
        st.error(f"Error adding sample data: {e}")
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
    
    # Show expected headers
    st.subheader("Expected PhantomBuster Headers")
    st.write(EXPECTED_HEADERS)
    
    # Compare headers
    st.subheader("Header Comparison")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Current Headers")
        if sheet_data["headers"]:
            for header in sheet_data["headers"]:
                if header in EXPECTED_HEADERS:
                    st.success(header)
                else:
                    st.error(header)
        else:
            st.warning("No headers found")
    
    with col2:
        st.write("Expected Headers")
        for header in EXPECTED_HEADERS:
            if sheet_data["headers"] and header in sheet_data["headers"]:
                st.success(header)
            else:
                st.warning(header)
    
    # Actions
    st.subheader("Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Sheet"):
            with st.spinner("Clearing sheet..."):
                success = clear_sheet(service)
                if success:
                    st.success("Sheet cleared successfully")
                    time.sleep(1)
                    st.rerun()
    
    with col2:
        if st.button("Update Headers"):
            with st.spinner("Updating headers..."):
                success = update_sheet_headers(service)
                if success:
                    st.success("Headers updated successfully")
                    time.sleep(1)
                    st.rerun()
    
    with col3:
        if st.button("Add Sample Data"):
            with st.spinner("Adding sample data..."):
                success = add_sample_data(service)
                if success:
                    st.success("Sample data added successfully")
                    time.sleep(1)
                    st.rerun()
    
    # All-in-one button
    if st.button("🔄 Fix Everything (Clear + Update Headers + Add Sample Data)", type="primary"):
        with st.spinner("Fixing everything..."):
            # Clear sheet
            st.write("Step 1: Clearing sheet...")
            clear_success = clear_sheet(service)
            if not clear_success:
                st.error("Failed to clear sheet")
                return
            
            # Update headers
            st.write("Step 2: Updating headers...")
            headers_success = update_sheet_headers(service)
            if not headers_success:
                st.error("Failed to update headers")
                return
            
            # Add sample data
            st.write("Step 3: Adding sample data...")
            data_success = add_sample_data(service)
            if not data_success:
                st.error("Failed to add sample data")
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

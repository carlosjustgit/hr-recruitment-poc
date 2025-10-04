"""
Fix Google Sheet for PhantomBuster

This script will:
1. Clear the entire sheet (including headers)
2. Add the correct headers PhantomBuster expects
3. Add sample LinkedIn URLs
4. Verify the data was written correctly
"""
import os
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import traceback

# Configuration
SHEET_ID = "12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ"
WORKSHEET_NAME = "candidatos"

# Sample LinkedIn URLs
SAMPLE_DATA = [
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
    }
]

def get_sheet_service():
    """Get Google Sheets service"""
    try:
        # Check if credentials file exists
        if not os.path.exists("service-account-key.json"):
            print("Service account key file not found")
            return None
            
        # Setup credentials
        credentials = Credentials.from_service_account_file(
            "service-account-key.json",
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error setting up Google Sheets service: {e}")
        traceback.print_exc()
        return None

def clear_sheet_data(service):
    """Clear all data from the sheet"""
    try:
        # Clear the entire worksheet
        clear_range = f"{WORKSHEET_NAME}!A1:ZZ1000"
        result = service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range=clear_range,
            body={}
        ).execute()
        
        cleared_range = result.get('clearedRange', '')
        print(f"Successfully cleared data from {cleared_range}")
        return True
            
    except Exception as e:
        print(f"Error clearing sheet data: {e}")
        traceback.print_exc()
        return False

def write_sample_data(service):
    """Write sample data to the Google Sheet"""
    try:
        # Define the headers - EXACTLY as PhantomBuster expects
        headers = ["Profile Url", "First Name", "Last Name"]
        
        # Convert sample data to rows
        rows = [headers]  # First row is headers
        for item in SAMPLE_DATA:
            row = [item.get(header, "") for header in headers]
            rows.append(row)
        
        # Write to sheet
        body = {'values': rows}
        result = service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"{WORKSHEET_NAME}!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Successfully wrote {len(rows)-1} rows to sheet")
        print(f"Updated range: {result.get('updatedRange')}")
        print(f"Updated rows: {result.get('updatedRows')}")
        print(f"Updated cells: {result.get('updatedCells')}")
        return True
        
    except Exception as e:
        print(f"Error writing to sheet: {e}")
        traceback.print_exc()
        return False

def read_sheet_data(service):
    """Read data from the Google Sheet"""
    try:
        # Get data from sheet
        sheet_range = f"{WORKSHEET_NAME}!A1:ZZ"
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=sheet_range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("No data found in sheet")
            return []
        
        # Print headers
        print(f"Headers: {values[0]}")
        
        # Print data
        print(f"Found {len(values)-1} data rows")
        for i, row in enumerate(values[1:5]):  # Print first 5 rows
            print(f"Row {i+1}: {row}")
        
        return values
        
    except Exception as e:
        print(f"Error reading sheet data: {e}")
        traceback.print_exc()
        return []

def main():
    """Main function"""
    print("=== Fix Google Sheet for PhantomBuster ===")
    
    # Get Google Sheets service
    print("\n1. Setting up Google Sheets service...")
    service = get_sheet_service()
    if not service:
        print("Failed to initialize Google Sheets service")
        return
    print("Google Sheets service initialized")
    
    # Clear sheet data
    print("\n2. Clearing all sheet data...")
    clear_result = clear_sheet_data(service)
    if not clear_result:
        print("Failed to clear sheet data")
        # Continue anyway
    
    # Write sample data
    print("\n3. Writing sample data...")
    write_result = write_sample_data(service)
    if not write_result:
        print("Failed to write sample data")
        return
    
    # Read back the data
    print("\n4. Reading back the data...")
    read_sheet_data(service)
    
    print("\n=== Fix Complete ===")
    print(f"Google Sheet URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    print("\nNow try running PhantomBuster with this sheet!")

if __name__ == "__main__":
    main()

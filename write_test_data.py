"""
Direct Test: Write Data to Google Sheet

This script will:
1. Clear the Google Sheet
2. Write sample data with correct column names
3. Verify the data was written
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

def clear_sheet(service):
    """Clear all data from the spreadsheet"""
    try:
        # Clear the entire worksheet
        clear_range = f"{WORKSHEET_NAME}!A1:ZZ1000"
        result = service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range=clear_range,
            body={}
        ).execute()
        
        # Debug info
        cleared_range = result.get('clearedRange', '')
        print(f"Successfully cleared data from {cleared_range}")
        return True
            
    except Exception as e:
        print(f"Error clearing sheet: {e}")
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

def create_worksheet_if_not_exists(service):
    """Create the worksheet if it doesn't exist"""
    try:
        # Get sheet metadata
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        
        # Check if worksheet exists
        worksheet_exists = False
        for sheet in sheets:
            if sheet.get("properties", {}).get("title") == WORKSHEET_NAME:
                worksheet_exists = True
                break
        
        if not worksheet_exists:
            # Create the worksheet
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': WORKSHEET_NAME
                    }
                }
            }]
            result = service.spreadsheets().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={'requests': requests}
            ).execute()
            
            print(f"Created worksheet '{WORKSHEET_NAME}'")
        else:
            print(f"Worksheet '{WORKSHEET_NAME}' already exists")
        
        return True
        
    except Exception as e:
        print(f"Error checking/creating worksheet: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("=== Direct Test: Write Data to Google Sheet ===")
    
    # Get Google Sheets service
    print("\n1. Setting up Google Sheets service...")
    service = get_sheet_service()
    if not service:
        print("Failed to initialize Google Sheets service")
        return
    print("Google Sheets service initialized")
    
    # Create worksheet if it doesn't exist
    print("\n2. Checking if worksheet exists...")
    create_worksheet_if_not_exists(service)
    
    # Clear the sheet
    print("\n3. Clearing the sheet...")
    clear_result = clear_sheet(service)
    if not clear_result:
        print("Failed to clear sheet")
    
    # Write sample data
    print("\n4. Writing sample data...")
    write_result = write_sample_data(service)
    if not write_result:
        print("Failed to write sample data")
    
    # Read back the data
    print("\n5. Reading back the data...")
    read_sheet_data(service)
    
    print("\n=== Test Complete ===")
    print(f"Google Sheet URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

if __name__ == "__main__":
    main()

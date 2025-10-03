# HR Recruitment Agent - PoC

A proof of concept for an AI-powered recruitment agent that allows users to:
1. Upload contacts
2. Add to a central spreadsheet
3. Enrich data via PhantomBuster
4. Query enriched data using natural language

## Features

- **Upload Contacts:** CSV or Excel files with candidate information
- **Google Sheets Integration:** Automatically add contacts to a central spreadsheet
- **PhantomBuster Integration:** Enrich data with LinkedIn information
- **Natural Language Search:** Find candidates using everyday language queries
- **Data Visualization:** View and manage candidate data

## Setup

### Prerequisites

- Python 3.10 or higher
- Google Cloud project with Sheets API enabled
- Service account with access to your Google Sheet
- PhantomBuster account with API key
- Google Sheet ID

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hr-recruitment-poc.git
cd hr-recruitment-poc
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your credentials:
```
PHANTOM_API_KEY=your_phantombuster_api_key
PHANTOM_AGENT_ID=your_phantombuster_agent_id
SHEET_ID=your_google_sheet_id
```

4. Place your Google service account key file as `service-account-key.json` in the project root.

### Running the App

```bash
streamlit run poc_demo.py
```

## Usage

1. **Upload & Enrich Tab:**
   - Upload your contacts CSV/Excel file
   - Add contacts to the spreadsheet
   - Trigger PhantomBuster to enrich data

2. **Search Candidates Tab:**
   - Use natural language to search for candidates
   - View detailed candidate profiles
   - Access LinkedIn profiles and spreadsheet data

3. **Data View Tab:**
   - View all candidate data in a table format
   - Refresh to get the latest data

## Deployment

This app can be deployed on Streamlit Cloud:
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add secrets for API keys and service account

## Important Note

⚠️ **PROOF OF CONCEPT:** This is a demo to showcase the functionality. In production, data sources should be official and consented.

## License

This project is intended for demonstration purposes only.
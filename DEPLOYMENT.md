# Deployment Guide for Streamlit Cloud

## Prerequisites
1. GitHub account with this repository
2. Streamlit Cloud account (free tier available at https://streamlit.io/cloud)
3. Google Cloud service account JSON file
4. OpenAI API key (optional, for AI-powered search)

## Step 1: Prepare Your Repository
✅ Already done! Your code is pushed to GitHub.

## Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io/
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure the app**:
   - Repository: `carlosjustgit/hr-recruitment-poc`
   - Branch: `main`
   - Main file path: `poc_demo.py`
   - App URL: Choose a custom URL or use the default

## Step 3: Configure Secrets

In the Streamlit Cloud dashboard, go to **App settings** → **Secrets** and add:

```toml
# OpenAI API Key (optional - for AI-powered candidate search)
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"

# Google Cloud Service Account (required - for Google Sheets access)
# Paste the entire contents of your service-account-key.json file below
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour actual private key here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

## Step 4: Update Code to Use Streamlit Secrets

The app needs to be updated to read the Google credentials from Streamlit secrets instead of the local file.

Update `poc_demo.py` to add this at the top (after imports):

```python
# Check if running on Streamlit Cloud
if "gcp_service_account" in st.secrets:
    # Running on Streamlit Cloud - use secrets
    from google.oauth2 import service_account
    import json
    
    # Create credentials from secrets
    credentials_dict = dict(st.secrets["gcp_service_account"])
    GCP_CREDENTIALS = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
else:
    # Running locally - use file
    GCP_CREDENTIALS = Credentials.from_service_account_file(
        "service-account-key.json",
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
```

## Step 5: Environment Variables Already Set

Your `.env` file contains:
- PhantomBuster credentials (hardcoded in app for demo)
- Google Sheet ID (hardcoded in app for demo)
- OpenAI API key (will be read from Streamlit secrets if available)

## What's Already Working

✅ Smart caching for duplicate LinkedIn profiles
✅ GPT-4o AI-powered candidate search
✅ PhantomBuster integration for LinkedIn scraping
✅ Google Sheets integration
✅ Beautiful UI with chat interface
✅ All data properly displayed
✅ Error handling and user feedback

## Post-Deployment Testing

1. Upload a CSV with LinkedIn URLs
2. Click "Add to Spreadsheet" and confirm
3. Click "Enrich with LinkedIn Data"
4. Wait for enrichment to complete
5. Go to "Search Candidates" tab
6. Try asking: "Quien trabajó en ACL?" or other questions
7. Check the "Data View" tab to see all enriched data

## Notes

- The app will work without OpenAI API key (falls back to keyword search)
- PhantomBuster has a limit of 1 parallel job on free tier
- Smart caching prevents duplicate enrichment runs
- Demo data is available for testing without API limits

## Support

For issues or questions about deployment, check:
- Streamlit Cloud documentation: https://docs.streamlit.io/streamlit-community-cloud
- This repository's README.md


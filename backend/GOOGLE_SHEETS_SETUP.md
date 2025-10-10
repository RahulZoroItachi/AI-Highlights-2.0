# Google Sheets Setup Instructions

To enable Google Sheets integration, follow these steps:

## 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click on it and enable it

## 2. Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "AIH V1 Sheets Integration")
5. Click "Create"

## 3. Download Credentials

1. Click the download button (⬇️) next to your new OAuth 2.0 Client ID
2. Save the file as `credentials.json` in the `backend/` folder
3. The file should look like this:
   ```json
   {
     "installed": {
       "client_id": "your-client-id.apps.googleusercontent.com",
       "project_id": "your-project-id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "your-client-secret",
       "redirect_uris": ["http://localhost"]
     }
   }
   ```

## 4. Install Dependencies

Run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

## 5. First Run

When you run the application for the first time with Google Sheets integration:

1. The application will open a browser window
2. Sign in to your Google account
3. Grant permissions to the application
4. A `token.json` file will be created automatically
5. This file will be used for future runs without requiring re-authentication

## 6. Usage

The application will automatically:
- Create a new Google Spreadsheet for each run
- Add each API response as a separate sheet
- Name sheets based on the answer_id and step title
- Provide a direct link to the created spreadsheet

## Troubleshooting

- If you get authentication errors, delete `token.json` and run again
- Make sure `credentials.json` is in the `backend/` folder
- Ensure the Google Sheets API is enabled in your project
- Check that your OAuth 2.0 Client ID is configured for desktop applications

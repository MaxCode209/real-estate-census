# Google Sheets Export Setup Guide

## ✅ What's Already Done

- ✅ Export code is implemented (`backend/routes.py`)
- ✅ Dependencies are in `requirements.txt`
- ✅ Frontend button is ready (map interface)
- ✅ API endpoint: `/api/export/sheets`

## 🔧 Step-by-Step Setup

### Step 1: Install Dependencies (if not already installed)

```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
```

### Step 2: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - URL: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project** (or use existing)
   - Click the project dropdown at the top
   - Click **"New Project"**
   - Name: `Real Estate Census Export` (or any name)
   - Click **"Create"**

### Step 3: Enable Google Sheets & Drive APIs

1. In the project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Sheets API"**
   - Click on it
   - Click **"Enable"**
3. Search for **"Google Drive API"**
   - Click on it
   - Click **"Enable"**

### Step 4: Create Service Account

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"Service account"**
4. Fill in:
   - **Service account name**: `census-export` (or any name)
   - **Service account ID**: (auto-filled)
   - Click **"Create and Continue"**
5. **Grant access** (optional - can skip):
   - Click **"Continue"**
   - Click **"Done"**

### Step 5: Create & Download JSON Key

1. In the **"Credentials"** page, find your service account
2. Click on the service account email (it will open details)
3. Go to **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Select **"JSON"** format
6. Click **"Create"**
   - This downloads a JSON file (e.g., `real-estate-census-export-xxxxx.json`)

### Step 6: Save Credentials File

1. **Create credentials directory** (if it doesn't exist):
   ```bash
   mkdir credentials
   ```

2. **Move the downloaded JSON file** to the credentials folder:
   - Rename it to: `google_sheets_credentials.json`
   - Place it at: `credentials/google_sheets_credentials.json`

   **On Windows (PowerShell):**
   ```powershell
   # If you downloaded to Downloads folder
   Move-Item "$env:USERPROFILE\Downloads\real-estate-census-export-*.json" "credentials\google_sheets_credentials.json"
   ```

### Step 7: Share Google Sheet with Service Account

**IMPORTANT**: The service account needs access to create/edit sheets.

1. Note the **"client_email"** from the JSON file (looks like: `census-export@project-name.iam.gserviceaccount.com`)
2. When the export creates a sheet, you'll need to share it with this email
3. **OR** create a folder in Google Drive, share it with the service account email (as Editor), and the export will create sheets there

**Alternative (Recommended)**: We can modify the code to automatically share the sheet with your email. Let me know if you want this!

### Step 8: Test the Export

1. **Start your Flask app:**
   ```bash
   python app.py
   ```

2. **Option A: Via Map Interface**
   - Go to: http://localhost:5000
   - Click **"Export to Google Sheets"** button
   - Check for success message with spreadsheet URL

3. **Option B: Via API (curl/PowerShell)**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/api/export/sheets" -Method Get
   ```

4. **Option C: Via Browser**
   - Go to: http://localhost:5000/api/export/sheets
   - You should see JSON with spreadsheet URL

## 📋 Quick Checklist

- [ ] Dependencies installed (`gspread`, `google-auth`, etc.)
- [ ] Google Cloud project created
- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled
- [ ] Service account created
- [ ] JSON key file downloaded
- [ ] JSON file saved as `credentials/google_sheets_credentials.json`
- [ ] Tested export functionality

## 🔍 Troubleshooting

### Error: "Credentials not found"
- Make sure file is at: `credentials/google_sheets_credentials.json`
- Check the filename is exactly correct
- Verify file exists: `ls credentials/` (or `dir credentials` on Windows)

### Error: "Permission denied" or "Access denied"
- Make sure Google Sheets API is enabled in your project
- Make sure Google Drive API is enabled
- Check that the JSON file is valid (open it to verify)

### Error: "Spreadsheet not found" or "Cannot create spreadsheet"
- The service account needs permissions to create files
- Try creating a Google Drive folder, sharing it with the service account email (as Editor), and modify code to create sheets in that folder

### Error: "Invalid credentials"
- Re-download the JSON key file
- Make sure you didn't modify the JSON file
- Verify the service account still exists in Google Cloud Console

## 🎯 Next Steps After Setup

Once working, you can:
1. Export all data: `GET /api/export/sheets`
2. Export with limit: `GET /api/export/sheets?limit=100`
3. Custom spreadsheet name: `GET /api/export/sheets?spreadsheet_name=My Data`
4. Use the button in the map interface

## 📝 Example Usage

**Export all 1,224 zip codes:**
```bash
curl http://localhost:5000/api/export/sheets
```

**Export first 100 records to custom sheet:**
```bash
curl "http://localhost:5000/api/export/sheets?limit=100&spreadsheet_name=Top 100 Zip Codes"
```

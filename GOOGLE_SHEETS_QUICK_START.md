# Google Sheets Export - Quick Start

## 🚀 Fast Setup (5 Minutes)

### Step 1: Get Google Cloud Credentials

1. **Go to**: https://console.cloud.google.com/
2. **Create or select a project**
3. **Enable APIs**:
   - Go to "APIs & Services" → "Library"
   - Search "Google Sheets API" → Enable
   - Search "Google Drive API" → Enable
4. **Create Service Account**:
   - Go to "APIs & Services" → "Credentials"
   - Click "+ CREATE CREDENTIALS" → "Service account"
   - Name: `census-export` (or any name)
   - Click "Create and Continue" → "Done"
5. **Download JSON Key**:
   - Click on your service account email
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key" → "JSON"
   - Save the downloaded file

### Step 2: Save Credentials File

**Rename and move the downloaded JSON file to:**
```
credentials/google_sheets_credentials.json
```

**On Windows PowerShell:**
```powershell
# If downloaded to Downloads folder
Move-Item "$env:USERPROFILE\Downloads\*.json" "credentials\google_sheets_credentials.json"
```

### Step 3: Verify Setup

```bash
python scripts/verify_sheets_setup.py
```

This will check if everything is configured correctly.

### Step 4: Test Export

**Start your app:**
```bash
python app.py
```

**Export via API:**
```powershell
# Export all data
Invoke-RestMethod -Uri "http://localhost:5000/api/export/sheets" -Method Get

# Or via browser
# Go to: http://localhost:5000/api/export/sheets
```

**Or use the map interface:**
- Go to: http://localhost:5000
- Click "Export to Sheets" button

## 📋 What Happens When You Export

1. Exports all 1,224 zip codes from your database
2. Creates a new Google Sheet named "Census Data Export" (or updates existing)
3. Creates a worksheet named "Census Data"
4. Writes all census data with headers

## ⚠️ Important Note

**The first time you export**, Google will create a new sheet. You'll need to:
1. Get the sheet URL from the response
2. Open the sheet in your browser
3. The sheet will be owned by the service account

**To access the sheet easily**, we can modify the code to automatically share it with your email. Just let me know!

## 🔍 Troubleshooting

### "Credentials not found"
- Make sure file is at: `credentials/google_sheets_credentials.json`
- Check the filename is exactly correct

### "Permission denied"
- Make sure both APIs are enabled (Sheets API + Drive API)
- Check that the JSON file is valid (open it - should be readable JSON)

### Need more help?
See `GOOGLE_SHEETS_SETUP.md` for detailed instructions.

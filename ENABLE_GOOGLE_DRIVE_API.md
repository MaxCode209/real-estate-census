# Enable Google Drive API - Quick Fix

## ⚠️ Error Fix

The error message tells you exactly what to do. Follow these steps:

### Step 1: Enable Google Drive API

**Click this link** (it's from your error message):
https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=111708603314

Or manually:
1. Go to: https://console.cloud.google.com/
2. Make sure project `census-data-483520` (ID: 111708603314) is selected
3. Go to: **"APIs & Services"** → **"Library"** (left sidebar)
4. Search for: **"Google Drive API"**
5. Click on **"Google Drive API"**
6. Click the **"Enable"** button

### Step 2: Verify Google Sheets API is Also Enabled

While you're there, make sure **Google Sheets API** is also enabled:
1. In **"APIs & Services"** → **"Library"**
2. Search for: **"Google Sheets API"**
3. If it says "Enabled", you're good
4. If it says "Enable", click it

### Step 3: Wait a Few Minutes

After enabling, Google says to wait a few minutes for changes to propagate. Usually it's instant, but sometimes takes 1-2 minutes.

### Step 4: Try Export Again

```bash
python app.py
```

Then test:
- Go to: http://localhost:5000/api/export/sheets
- Or click "Export to Sheets" button in the map interface

## Quick Checklist

- [ ] Google Drive API enabled
- [ ] Google Sheets API enabled  
- [ ] Waited 1-2 minutes after enabling
- [ ] Tried export again

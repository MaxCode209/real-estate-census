# Test Google Sheets Export

## ✅ APIs Enabled
- Google Drive API: ✅ Enabled
- Google Sheets API: ✅ Enabled

## 🚀 Test Export

### Option 1: Start App and Test via Browser

1. **Start your Flask app** (if not running):
   ```bash
   python app.py
   ```

2. **Test export via browser:**
   - Go to: http://localhost:5000/api/export/sheets
   - You should see JSON response with spreadsheet URL

3. **Or use the map interface:**
   - Go to: http://localhost:5000
   - Click "Export to Google Sheets" button
   - Check for success message

### Option 2: Test via PowerShell

```powershell
# Make sure app is running first, then:
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/export/sheets" -Method Get
$response | ConvertTo-Json -Depth 10
```

### Option 3: Test with Custom Options

```powershell
# Export with limit
Invoke-RestMethod -Uri "http://localhost:5000/api/export/sheets?limit=100" -Method Get

# Export with custom spreadsheet name
Invoke-RestMethod -Uri "http://localhost:5000/api/export/sheets?spreadsheet_name=My%20Census%20Data" -Method Get
```

## 📋 Expected Response

If successful, you'll see:
```json
{
  "message": "Data exported to Google Sheets",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/...",
  "records_exported": 1224
}
```

## ⚠️ First Time Access

The first time you export:
- Google will create a new sheet owned by the service account
- The sheet URL will be in the response
- You may need to share the sheet with your email to access it easily

We can modify the code to auto-share with your email if needed!

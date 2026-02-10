# Google Sheets Setup - Service Account (NOT OAuth)

## ⚠️ Important: You Don't Need OAuth Client ID!

For this application, we use a **Service Account** (not OAuth Client ID). Here's why:

- **OAuth Client ID**: For apps where users log in with Google
- **Service Account**: For server-to-server authentication (what we need)

## ✅ Correct Setup Steps

### Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click the project dropdown at the top
3. Click **"New Project"**
   - Name: `Real Estate Census Export`
   - Click **"Create"**

### Step 2: Enable Required APIs

1. In your project, go to **"APIs & Services"** → **"Library"** (left sidebar)
2. Search for **"Google Sheets API"**
   - Click on it
   - Click **"Enable"** button
3. Search for **"Google Drive API"**
   - Click on it
   - Click **"Enable"** button

### Step 3: Create Service Account (THIS IS WHAT YOU NEED!)

**NOT OAuth Client ID - Create a Service Account:**

1. Go to **"APIs & Services"** → **"Credentials"** (left sidebar)
2. At the top, click **"+ CREATE CREDENTIALS"**
3. In the dropdown, select **"Service account"** (NOT "OAuth client ID")
4. Fill in the form:
   - **Service account name**: `census-export` (or any name you like)
   - **Service account ID**: (auto-filled, leave as is)
   - Click **"Create and Continue"**
5. **Optional - Grant access**: 
   - You can skip this for now (click "Continue" → "Done")
   - Or assign a role like "Editor" if you want

### Step 4: Create and Download Key

1. After creating the service account, you'll see a list
2. **Click on the service account email** (the one you just created)
   - It looks like: `census-export@your-project-id.iam.gserviceaccount.com`
3. In the service account details page:
   - Click the **"Keys"** tab at the top
   - Click **"Add Key"** → **"Create new key"**
   - Select **"JSON"** as the key type
   - Click **"Create"**
4. **The JSON file will download automatically**
   - It has a name like: `your-project-id-xxxxx.json`

### Step 5: Save the Credentials File

1. **Rename the downloaded file** to: `google_sheets_credentials.json`
2. **Move it to your project's credentials folder**:
   ```
   credentials/google_sheets_credentials.json
   ```

**On Windows PowerShell:**
```powershell
# Navigate to your project
cd "C:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Site Selection Process"

# Move the downloaded file (adjust path if needed)
Move-Item "$env:USERPROFILE\Downloads\your-project-id-*.json" "credentials\google_sheets_credentials.json"

# Or if you know the exact filename:
Move-Item "C:\Users\Max\Downloads\your-project-id-xxxxx.json" "credentials\google_sheets_credentials.json"
```

### Step 6: Verify Setup

Run the verification script:
```bash
python scripts/verify_sheets_setup.py
```

You should see:
```
[OK] gspread installed
[OK] google-auth installed
[OK] Credentials file found
[OK] Credentials file is valid JSON
[OK] Authentication successful
[SUCCESS] SETUP COMPLETE!
```

## 📋 Visual Guide - What to Look For

### ✅ CORRECT: Service Account (What You Need)
- Location: "APIs & Services" → "Credentials"
- Button: "+ CREATE CREDENTIALS" → **"Service account"**
- Result: A JSON key file downloads

### ❌ WRONG: OAuth Client ID (Don't Use This)
- This is for user login flows
- Creates a different type of credential
- Won't work for our server-to-server export

## 🔍 Troubleshooting

### "I only see OAuth Client ID option"
- Make sure you clicked "Service account" (not "API Key" or "OAuth client ID")
- It's in the dropdown menu under "CREATE CREDENTIALS"

### "I don't see Service Account option"
- Make sure you're in "APIs & Services" → "Credentials" (not "OAuth consent screen")
- The button is at the top: "+ CREATE CREDENTIALS"
- The dropdown should show: "API key", "OAuth client ID", **"Service account"**

### "Where is the JSON file?"
- It downloads automatically when you click "Create" in Step 4
- Check your Downloads folder
- Look for a file named something like: `your-project-name-xxxxx.json`

### "The service account email looks weird"
- That's normal! It looks like: `census-export@project-id.iam.gserviceaccount.com`
- This is correct - it's not a real email address

## ✅ Quick Checklist

- [ ] Google Cloud project created
- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled
- [ ] Service Account created (NOT OAuth Client ID)
- [ ] JSON key file downloaded
- [ ] File saved as `credentials/google_sheets_credentials.json`
- [ ] Verification script passes

## 🎯 What the JSON File Should Look Like

The file should start like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "census-export@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  ...
}
```

If your file has `"type": "service_account"`, you're good!

## 🚀 After Setup

Once the credentials file is in place, you can export:

```bash
# Start your app
python app.py

# Export via API
curl http://localhost:5000/api/export/sheets

# Or use the map interface
# Go to: http://localhost:5000
# Click "Export to Sheets" button
```

# Fix Google Drive Storage Quota Issue

## ⚠️ Error: Drive Storage Quota Exceeded

The service account has limited Drive storage. Here are solutions:

## ✅ Solution 1: Share a Folder with Service Account (RECOMMENDED)

This is the easiest fix:

1. **Create a Google Drive folder** (or use an existing one)
   - Go to: https://drive.google.com/
   - Create a new folder (e.g., "Census Data Exports")

2. **Share the folder with your service account:**
   - Right-click the folder → "Share"
   - Add this email: `census-export@census-data-483520.iam.gserviceaccount.com`
   - Set permission: **"Editor"**
   - Click "Send" (or "Share")

3. **Get the folder ID:**
   - Open the folder in Google Drive
   - Look at the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
   - Copy the `FOLDER_ID_HERE` part

4. **We'll update the code to use this folder** (I can do this for you)

## ✅ Solution 2: Export to Existing Spreadsheet

Instead of creating a new sheet, we can export to an existing one:

1. **Create a Google Sheet manually:**
   - Go to: https://sheets.google.com/
   - Create a new spreadsheet
   - Name it: "Census Data Export"

2. **Share it with the service account:**
   - Click "Share" button
   - Add: `census-export@census-data-483520.iam.gserviceaccount.com`
   - Set permission: **"Editor"**
   - Click "Send"

3. **The code will then find and update this existing sheet**

## ✅ Solution 3: Modify Code to Use Shared Folder

I can update the export code to automatically create sheets in a shared folder. Just provide:
- The folder ID (from Solution 1)

## 📋 Quick Steps to Share Folder

1. Go to Google Drive
2. Create or select a folder
3. Right-click → "Share"
4. Add email: `census-export@census-data-483520.iam.gserviceaccount.com`
5. Permission: "Editor"
6. Click "Share"

Then let me know the folder ID, and I'll update the code!

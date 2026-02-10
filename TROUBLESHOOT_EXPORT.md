# Troubleshooting Google Sheets Export

## Current Issue: Drive Storage Quota Exceeded

The export is failing with a quota error. Here's how to fix it:

## Step 1: Verify Folder Sharing ✅

1. **Open the folder:**
   - https://drive.google.com/drive/folders/11cvUOj37sPLcRIclVHCRfHt3fWcl7n75

2. **Check sharing:**
   - Right-click the folder → "Share"
   - Look for this email: `census-export@census-data-483520.iam.gserviceaccount.com`
   - Make sure it has **"Editor"** permission
   - If it's not there, add it now

## Step 2: Check Your Drive Storage 📊

1. **Check storage:**
   - Go to: https://drive.google.com/settings/storage
   - See how much space you have available

2. **If full, free up space:**
   - Delete old files
   - Empty trash
   - Need at least a few MB free

## Step 3: Test Folder Permissions 🔍

1. **Create a test sheet manually:**
   - Go to: https://drive.google.com/
   - Create a new Google Sheet
   - Move it into the folder: 11cvUOj37sPLcRIclVHCRfHt3fWcl7n75
   - Share the sheet with: `census-export@census-data-483520.iam.gserviceaccount.com` (Editor)

2. **If this works, the issue is with creating new files**
3. **If this fails, the issue is with permissions**

## Alternative Solution: Use Existing Sheet 📝

Instead of creating a new sheet each time, we can:

1. **You create a Google Sheet manually:**
   - Name it: "Census Data Export"
   - Put it in the shared folder
   - Share with service account (Editor)

2. **Code will find and update this existing sheet**

Let me know if you want to try this approach instead!

## Quick Checklist

- [ ] Folder shared with service account email
- [ ] Service account has "Editor" permission
- [ ] You have free Drive storage space
- [ ] Can manually create files in the folder

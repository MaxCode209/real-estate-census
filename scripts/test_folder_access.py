"""Test if service account can access the shared folder."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.config import Config
import json

def test_folder_access():
    """Test if service account can access and list files in the folder."""
    folder_id = '11cvUOj37sPLcRIclVHCRfHt3fWcl7n75'
    
    # Load credentials
    creds_path = Config.GOOGLE_SHEETS_CREDENTIALS_PATH
    if not os.path.exists(creds_path):
        print(f"ERROR: Credentials file not found: {creds_path}")
        return False
    
    creds = Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Test 1: List files in the folder
        print("Test 1: Listing files in folder...")
        print(f"Folder ID: {folder_id}")
        print(f"Service Account: {creds.service_account_email}")
        print()
        
        try:
            results = drive_service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType)",
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            print(f"[OK] Found {len(files)} files in folder")
            for file in files:
                print(f"  - {file['name']} ({file['mimeType']})")
            
        except Exception as e:
            print(f"[ERROR] Cannot list files: {e}")
            return False
        
        # Test 2: Get folder info
        print("\nTest 2: Getting folder info...")
        try:
            folder = drive_service.files().get(
                fileId=folder_id,
                fields="id, name, permissions, owners"
            ).execute()
            
            print(f"[OK] Folder name: {folder.get('name', 'N/A')}")
            print(f"[OK] Folder ID: {folder.get('id', 'N/A')}")
            
            # Check permissions
            if 'permissions' in folder:
                print(f"\nFolder has {len(folder['permissions'])} permissions")
                for perm in folder['permissions']:
                    email = perm.get('emailAddress', perm.get('id', 'N/A'))
                    role = perm.get('role', 'N/A')
                    print(f"  - {email}: {role}")
                    if email == creds.service_account_email:
                        print(f"    [OK] Service account found with role: {role}")
            
        except Exception as e:
            print(f"[ERROR] Cannot get folder info: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 3: Try creating a small test file
        print("\nTest 3: Attempting to create a test file...")
        try:
            file_metadata = {
                'name': 'TEST_EXPORT_DELETE_ME',
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [folder_id]
            }
            
            file = drive_service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            print(f"[SUCCESS] Created test file: {file['name']}")
            print(f"  File ID: {file['id']}")
            print(f"  URL: {file['webViewLink']}")
            print("\n  [INFO] This test file was created successfully!")
            print("  [INFO] You can delete it manually from Google Drive")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Cannot create file: {e}")
            
            # Try to get detailed error
            if hasattr(e, 'content'):
                try:
                    error_json = json.loads(e.content.decode('utf-8'))
                    print("\nDetailed error:")
                    print(json.dumps(error_json, indent=2))
                except:
                    print(f"Raw error content: {e.content}")
            
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"[ERROR] General error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Service Account Folder Access")
    print("=" * 60)
    print()
    
    success = test_folder_access()
    
    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAILED] Some tests failed. Check output above.")
    print("=" * 60)

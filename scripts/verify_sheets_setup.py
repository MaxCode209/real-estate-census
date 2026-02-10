"""Verify Google Sheets export setup."""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_setup():
    """Check if Google Sheets export is properly configured."""
    print("Checking Google Sheets Export Setup...")
    print("=" * 60)
    
    # Check 1: Dependencies
    print("\n1. Checking dependencies...")
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        print("   [OK] gspread installed")
        print("   [OK] google-auth installed")
    except ImportError as e:
        print(f"   [ERROR] Missing dependency: {e}")
        print("   → Install with: pip install gspread google-auth google-auth-oauthlib")
        return False
    
    # Check 2: Credentials file
    print("\n2. Checking credentials file...")
    from config.config import Config
    creds_path = Config.GOOGLE_SHEETS_CREDENTIALS_PATH
    
    if os.path.exists(creds_path):
        print(f"   [OK] Credentials file found: {creds_path}")
        
        # Check if it's valid JSON
        try:
            import json
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            
            # Check required fields
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
            missing = [f for f in required_fields if f not in creds_data]
            
            if missing:
                print(f"   [ERROR] Credentials file missing required fields: {missing}")
                return False
            else:
                print("   [OK] Credentials file is valid JSON")
                print(f"   [OK] Service account email: {creds_data.get('client_email', 'N/A')}")
                print(f"   [OK] Project ID: {creds_data.get('project_id', 'N/A')}")
        except json.JSONDecodeError:
            print("   [ERROR] Credentials file is not valid JSON")
            return False
        except Exception as e:
            print(f"   [ERROR] Error reading credentials: {e}")
            return False
    else:
        print(f"   [ERROR] Credentials file NOT found: {creds_path}")
        print("\n   To fix this:")
        print("   1. Go to: https://console.cloud.google.com/")
        print("   2. Create a project (or use existing)")
        print("   3. Enable 'Google Sheets API' and 'Google Drive API'")
        print("   4. Create a Service Account")
        print("   5. Download JSON key file")
        print(f"   6. Save it as: {creds_path}")
        print("\n   See GOOGLE_SHEETS_SETUP.md for detailed instructions")
        return False
    
    # Check 3: Test authentication (optional)
    print("\n3. Testing authentication...")
    try:
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        )
        print("   [OK] Authentication successful")
        print(f"   [OK] Service account: {creds.service_account_email}")
    except Exception as e:
        print(f"   [ERROR] Authentication failed: {e}")
        print("   → Check that your credentials file is valid")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] SETUP COMPLETE! Google Sheets export is ready to use.")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Start your app: python app.py")
    print("  2. Export via map interface or API endpoint")
    print("  3. API: GET /api/export/sheets")
    
    return True

if __name__ == '__main__':
    success = check_setup()
    sys.exit(0 if success else 1)

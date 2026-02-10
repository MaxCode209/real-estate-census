"""Helper script to create .env file interactively."""
import os

def create_env_file():
    """Create .env file with user input."""
    print("Setting up environment configuration...")
    print("Press Enter to use default values (shown in brackets)\n")
    
    # Database
    db_url = input("Database URL [postgresql://localhost:5432/real_estate_census]: ").strip()
    if not db_url:
        db_url = "postgresql://localhost:5432/real_estate_census"
    
    # Google Maps API Key
    maps_key = input("Google Maps API Key (required): ").strip()
    if not maps_key:
        print("Warning: Google Maps API Key is required for the map to work!")
    
    # Census API Key
    census_key = input("Census Bureau API Key (optional): ").strip()
    
    # Secret Key
    import secrets
    secret_key = secrets.token_hex(32)
    print(f"\nGenerated secret key: {secret_key[:20]}...")
    
    # Google Sheets credentials path
    sheets_path = input("Google Sheets credentials path [credentials/google_sheets_credentials.json]: ").strip()
    if not sheets_path:
        sheets_path = "credentials/google_sheets_credentials.json"
    
    # Create .env file
    env_content = f"""# Database Configuration
DATABASE_URL={db_url}

# Google Maps API Key
GOOGLE_MAPS_API_KEY={maps_key}

# Census Bureau API Key (optional but recommended)
CENSUS_API_KEY={census_key}

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY={secret_key}

# Google Sheets API (for export functionality)
GOOGLE_SHEETS_CREDENTIALS_PATH={sheets_path}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✓ .env file created successfully!")
    print("\nNext steps:")
    print("1. Initialize database: python scripts/init_db.py")
    print("2. Fetch census data: python scripts/fetch_census_data.py")
    print("3. Run application: python app.py")

if __name__ == '__main__':
    if os.path.exists('.env'):
        response = input(".env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            exit(0)
    
    create_env_file()


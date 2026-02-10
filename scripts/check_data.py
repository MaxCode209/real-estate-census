"""Check if data exists in the database."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine
from sqlalchemy import text

def check_data():
    """Check if census data exists."""
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'census_data'
                );
            """))
            table_exists = result.fetchone()[0]
            
            if not table_exists:
                print("Table 'census_data' does not exist.")
                print("Run: python scripts/init_db.py")
                return False
            
            # Check record count
            result = conn.execute(text("SELECT COUNT(*) FROM census_data"))
            count = result.fetchone()[0]
            
            print(f"Records in database: {count}")
            
            if count == 0:
                print("\nDatabase is empty. You need to fetch census data.")
                print("Run: python scripts/fetch_census_data.py")
                return False
            else:
                print(f"\nDatabase has {count} zip code records. Ready to use!")
                return True
                
    except Exception as e:
        print(f"Error checking data: {str(e)}")
        return False

if __name__ == '__main__':
    if not os.path.exists('.env'):
        print("Error: .env file not found!")
        print("Please run: python scripts/setup_env.py")
        sys.exit(1)
    
    success = check_data()
    sys.exit(0 if success else 1)

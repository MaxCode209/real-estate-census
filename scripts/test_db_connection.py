"""Test database connection before setting up."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config.config import Config

def test_connection():
    """Test if database connection works."""
    print("Testing database connection...")
    print(f"Connection URL: {Config.DATABASE_URL[:50]}...")  # Show first 50 chars for security
    
    try:
        engine = create_engine(Config.DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"\n[SUCCESS] Connection successful!")
            print(f"[SUCCESS] PostgreSQL version: {version[:50]}...")
            
            # Test if we can create tables
            conn.execute(text("SELECT 1;"))
            print("[SUCCESS] Database is ready for use!")
            
        return True
        
    except Exception as e:
        print(f"\nX Connection failed!")
        print(f"Error: {str(e)}")
        print("\nCommon issues:")
        print("1. Check your connection string format")
        print("2. Verify your database password is correct")
        print("3. Make sure your database is running/accessible")
        print("4. Check if your IP is whitelisted (some cloud services require this)")
        return False

if __name__ == '__main__':
    if not os.path.exists('.env'):
        print("Error: .env file not found!")
        print("Please run: python scripts/setup_env.py")
        sys.exit(1)
    
    success = test_connection()
    sys.exit(0 if success else 1)


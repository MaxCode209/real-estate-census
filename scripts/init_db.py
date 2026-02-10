"""Initialize the database with required tables."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, engine
from backend.models import CensusData

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print(f"Database URL: {str(engine.url).split('@')[1] if '@' in str(engine.url) else 'configured'}")


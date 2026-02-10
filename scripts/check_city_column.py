"""Quick check: does census_data have a 'city' column?"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from config.config import Config

def main():
    engine = create_engine(Config.DATABASE_URL, pool_size=1, max_overflow=0, connect_args={"connect_timeout": 15})
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'census_data' AND column_name = 'city'
        """))
        row = r.fetchone()
    print("Column 'city' exists in census_data." if row else "Column 'city' NOT found.")
    return 0 if row else 1

if __name__ == "__main__":
    sys.exit(main())

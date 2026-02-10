"""Add city column only - single ALTER, no index. Run: python scripts/add_city_column_only.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from config.config import Config

def main():
    engine = create_engine(Config.DATABASE_URL, pool_size=1, max_overflow=0, connect_args={"connect_timeout": 20})
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE census_data ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL"))
        conn.commit()
    print("Done. Column 'city' added (or already existed).")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

"""
Print census_data table schema and row count (read-only).
Run this and paste the output when we need to "see" columns or confirm migrations.
  python scripts/describe_census_schema.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from config.config import Config

def main():
    engine = create_engine(Config.DATABASE_URL, connect_args={"connect_timeout": 15})
    with engine.connect() as conn:
        # Row count
        r = conn.execute(text("SELECT COUNT(*) FROM census_data"))
        n = r.scalar()
        print("census_data row count:", n)

        # Columns
        r = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'census_data'
            ORDER BY ordinal_position
        """))
        rows = r.fetchall()
        print("\nColumns:")
        for row in rows:
            print(f"  {row[0]}: {row[1]} (nullable={row[2]})")

        # Sample row (optional; only zip_code/population so it works before 'city' exists)
        r = conn.execute(text("SELECT zip_code, population FROM census_data LIMIT 1"))
        row = r.fetchone()
        if row:
            print("\nSample row (zip_code, population):", row)

if __name__ == "__main__":
    main()

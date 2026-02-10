"""
Migration: Rename average_household_income -> median_household_income,
           drop state and county columns from census_data.
Run once before or after refreshing 2024 data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.database import engine

def run_migration():
    print("=" * 60)
    print("CENSUS DATA: Rename MHI column, drop state/county")
    print("=" * 60)

    with engine.connect() as conn:
        # 1. Rename average_household_income -> median_household_income
        try:
            conn.execute(text("""
                ALTER TABLE census_data
                RENAME COLUMN average_household_income TO median_household_income
            """))
            conn.commit()
            print("  [OK] Renamed average_household_income -> median_household_income")
        except Exception as e:
            if "does not exist" in str(e) or "already exists" in str(e):
                print("  [--] Column rename skipped (already done or column missing):", str(e)[:80])
            else:
                raise
            conn.rollback()

        # 2. Drop state column
        try:
            conn.execute(text("ALTER TABLE census_data DROP COLUMN IF EXISTS state"))
            conn.commit()
            print("  [OK] Dropped column state")
        except Exception as e:
            print("  [--] Drop state:", str(e)[:80])
            conn.rollback()

        # 3. Drop county column
        try:
            conn.execute(text("ALTER TABLE census_data DROP COLUMN IF EXISTS county"))
            conn.commit()
            print("  [OK] Dropped column county")
        except Exception as e:
            print("  [--] Drop county:", str(e)[:80])
            conn.rollback()

    print("=" * 60)
    print("Migration complete. Run: python scripts/fetch_census_data.py --from-db --refresh")
    print("=" * 60)

if __name__ == '__main__':
    run_migration()

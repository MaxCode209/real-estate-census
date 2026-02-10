"""
Verify census_data table: 2024 completeness and nulls.
Reports counts and lists zip codes with missing data so you can backfill.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func
from backend.database import SessionLocal
from backend.models import CensusData

# Columns that should be non-null for "complete" 2024 data (except net_migration_yoy which needs 2023)
REQUIRED_2024_COLUMNS = [
    'population',
    'median_age',
    'average_household_income',
    'total_households',
    'owner_occupied_units',
    'renter_occupied_units',
    'moved_from_different_state',
    'moved_from_different_county',
    'moved_from_abroad',
]
# net_migration_yoy can be null if no 2023 data; we still report it
OPTIONAL_2024_COLUMNS = ['net_migration_yoy']


def run_verify(backfill_zips=False):
    """Check 2024 rows for nulls and report. If backfill_zips=True, print zips to re-fetch."""
    db = SessionLocal()
    try:
        # All rows (we treat as 2024-focused; data_year may vary)
        total = db.query(CensusData).count()
        with_2024 = db.query(CensusData).filter(CensusData.data_year == '2024').count()
        with_pop = db.query(CensusData).filter(
            CensusData.data_year == '2024',
            CensusData.population.isnot(None),
            CensusData.population > 0,
        ).count()

        print("=== Census data summary ===")
        print(f"  Total rows: {total}")
        print(f"  Rows with data_year = 2024: {with_2024}")
        print(f"  Rows with data_year = 2024 and population > 0: {with_pop}")

        # Per-column null counts
        print("\n=== Null counts (data_year = 2024) ===")
        for col in REQUIRED_2024_COLUMNS + OPTIONAL_2024_COLUMNS:
            col_attr = getattr(CensusData, col)
            null_count = db.query(func.count(CensusData.id)).filter(
                CensusData.data_year == '2024',
                col_attr.is_(None),
            ).scalar()
            print(f"  {col}: {null_count} nulls")

        # Zip codes missing ANY required column (any null in required columns)
        rows_2024 = db.query(CensusData).filter(CensusData.data_year == '2024').all()
        zips_missing_any = []
        for row in rows_2024:
            for col in REQUIRED_2024_COLUMNS:
                if getattr(row, col) is None:
                    zips_missing_any.append(row.zip_code)
                    break
        zips_missing_any = sorted(set(zips_missing_any))

        print(f"\n  Zip codes missing at least one required column: {len(zips_missing_any)}")
        if zips_missing_any and len(zips_missing_any) <= 50:
            print("  " + ", ".join(zips_missing_any))
        elif zips_missing_any:
            print("  (First 50: " + ", ".join(zips_missing_any[:50]) + ", ...)")

        # net_migration_yoy: expected null when no 2023 data
        net_null = db.query(func.count(CensusData.id)).filter(
            CensusData.data_year == '2024',
            CensusData.net_migration_yoy.is_(None),
        ).scalar()
        print(f"\n  net_migration_yoy null (expected when no 2023 population): {net_null}")

        if backfill_zips and zips_missing_any:
            print("\n=== Re-fetch these zip codes ===")
            print("  python scripts/fetch_census_data.py --zip-codes " + " ".join(zips_missing_any[:100]))
            if len(zips_missing_any) > 100:
                print("  (Only first 100 shown; run verify again and use --backfill to get a batch)")

        return len(zips_missing_any)
    finally:
        db.close()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Verify census_data 2024 completeness')
    p.add_argument('--backfill', action='store_true', help='Print zip codes to re-fetch for missing data')
    args = p.parse_args()
    run_verify(backfill_zips=args.backfill)

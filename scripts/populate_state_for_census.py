"""
Populate census_data.state from zip codes using zipcodes package.

Requires: pip install zipcodes
Run after migration 20260214000000_add_state_to_census_data.sql

  python scripts/populate_state_for_census.py
  python scripts/populate_state_for_census.py --dry-run
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import zipcodes
except ImportError:
    print("Install zipcodes: pip install zipcodes")
    sys.exit(1)

from sqlalchemy import text
from backend.database import SessionLocal


def main():
    parser = argparse.ArgumentParser(description="Populate census_data.state from zip codes")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    args = parser.parse_args()

    db = SessionLocal()

    try:
        # Check if state column exists
        r = db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'census_data' AND column_name = 'state'"
        )).fetchone()
        if not r:
            print("ERROR: census_data.state column not found. Run migration first:")
            print("  supabase/migrations/20260214000000_add_state_to_census_data.sql")
            sys.exit(1)

        zips = db.execute(text("SELECT zip_code FROM census_data")).fetchall()
        total = len(zips)
        updated = 0
        skipped = 0

        for i, (zip_code,) in enumerate(zips):
            if (i + 1) % 5000 == 0:
                print(f"  Progress: {i+1}/{total}...")

            try:
                matches = zipcodes.matching(str(zip_code).strip())
            except (ValueError, TypeError):
                skipped += 1
                continue
            if matches and len(matches) > 0:
                state = matches[0].get("state", "").strip().upper()[:2]
                if state:
                    if not args.dry_run:
                        db.execute(
                            text("UPDATE census_data SET state = :s WHERE zip_code = :z"),
                            {"s": state, "z": zip_code}
                        )
                    updated += 1
                else:
                    skipped += 1
            else:
                skipped += 1

        if not args.dry_run:
            db.commit()
            print(f"\nUpdated {updated} rows with state. Skipped {skipped} (no lookup).")
        else:
            print(f"\n[DRY RUN] Would update {updated}. Skipped {skipped}.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

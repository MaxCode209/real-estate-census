"""
Update census_data.city from a CSV file.
CSV must have columns: zip_code, city (or 'city' as header for the city column).

Usage:
  python scripts/assign_city_from_csv.py [path/to/file.csv]

Default path: data/zip_codes_for_city.csv (from export_zips_for_city.py).
"""
import sys
import os
import csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData


def main():
    default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "zip_codes_for_city.csv")
    path = sys.argv[1] if len(sys.argv) > 1 else default_path

    if not os.path.isfile(path):
        print(f"File not found: {path}")
        print("Usage: python scripts/assign_city_from_csv.py [path/to/file.csv]")
        print("Or create data/zip_codes_for_city.csv by running: python scripts/export_zips_for_city.py")
        sys.exit(1)

    db = SessionLocal()
    updated = 0
    skipped = 0
    errors = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "zip_code" not in reader.fieldnames or "city" not in reader.fieldnames:
                print("CSV must have headers: zip_code, city")
                sys.exit(1)
            for row in reader:
                zip_code = (row.get("zip_code") or "").strip()
                city = (row.get("city") or "").strip()
                if not zip_code:
                    skipped += 1
                    continue
                try:
                    rec = db.query(CensusData).filter(CensusData.zip_code == zip_code).first()
                    if rec:
                        rec.city = city if city else None
                        db.add(rec)
                        updated += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append((zip_code, str(e)))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()

    print(f"Updated city for {updated} zip code(s).")
    if skipped:
        print(f"Skipped {skipped} row(s) (empty zip or not in census_data).")
    if errors:
        print(f"Errors: {len(errors)}")
        for z, msg in errors[:10]:
            print(f"  {z}: {msg}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")


if __name__ == "__main__":
    main()

"""
Export all zip_code rows from census_data to a CSV so you can add a 'city' column.
Output: data/zip_codes_for_city.csv (zip_code, city).
Edit the CSV: fill in the 'city' column for each zip, then run assign_city_from_csv.py.
"""
import sys
import os
import csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData


def main():
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "zip_codes_for_city.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    db = SessionLocal()
    try:
        rows = db.query(CensusData.zip_code, CensusData.city).order_by(CensusData.zip_code).all()
    finally:
        db.close()

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["zip_code", "city"])
        for zip_code, city in rows:
            w.writerow([zip_code, city or ""])

    print(f"Exported {len(rows)} rows to {out_path}")
    print("Next: open the CSV, fill in the 'city' column for each zip, then run:")
    print("  python scripts/assign_city_from_csv.py")


if __name__ == "__main__":
    main()

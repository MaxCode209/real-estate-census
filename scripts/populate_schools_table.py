"""
Populate the canonical schools table from school_data (and NCES when address missing).

Run this AFTER populate_school_addresses_from_nces.py has finished (so school_data
has as many addresses as possible).

For each unique (name, level) in school_data:
- Prefer address from school_data columns (elementary_school_address etc) if populated
- Else call NCES API for address, lat, lng
- Rating: MAX from school_data
- INSERT or UPDATE schools table

Usage:
    python scripts/populate_schools_table.py
    python scripts/populate_schools_table.py --limit 100 --dry-run
    python scripts/populate_schools_table.py --refresh   # Re-fetch from NCES even when we have address
"""
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text

from backend.database import SessionLocal
from backend.nces_client import search_school_by_name


def parse_zip_from_address(addr: str) -> Optional[str]:
    if not addr:
        return None
    m = re.search(r"\b(\d{5})(?:-\d{4})?\b", str(addr))
    return m.group(1) if m else None


def get_unique_schools_with_best_data(db) -> List[Tuple[str, str, Optional[str], Optional[float]]]:
    """Returns list of (name, level, best_address, best_rating)."""
    result = []
    for level, name_col, addr_col, rating_col in [
        ("elementary", "elementary_school_name", "elementary_school_address", "elementary_school_rating"),
        ("middle", "middle_school_name", "middle_school_address", "middle_school_rating"),
        ("high", "high_school_name", "high_school_address", "high_school_rating"),
    ]:
        sql = f"""
            SELECT {name_col} AS name, {addr_col} AS addr, {rating_col} AS rating
            FROM school_data
            WHERE {name_col} IS NOT NULL AND {rating_col} IS NOT NULL
        """
        rows = db.execute(text(sql)).fetchall()
        by_name: Dict[str, Tuple[Optional[str], float]] = {}
        for r in rows:
            name = str(r[0]).strip()
            addr = str(r[1]).strip() if r[1] and str(r[1]).strip() else None
            rating = float(r[2]) if r[2] is not None else None
            if name and rating is not None:
                existing = by_name.get(name)
                if existing is None:
                    by_name[name] = (addr, rating)
                else:
                    ex_addr, ex_rating = existing
                    if rating > ex_rating or (rating == ex_rating and addr and not ex_addr):
                        by_name[name] = (addr, rating)
        for name, (addr, rating) in by_name.items():
            result.append((name, level, addr, rating))
    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--refresh", action="store_true", help="Re-fetch from NCES even when address exists")
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        schools_data = get_unique_schools_with_best_data(db)
        if args.limit:
            schools_data = schools_data[: args.limit]

        total = len(schools_data)
        print(f"Found {total} unique schools to populate")

        if total == 0:
            print("Nothing to do.")
            return

        if args.dry_run:
            for name, level, addr, rating in schools_data[:5]:
                print(f"  {name} ({level}) addr={bool(addr)} rating={rating}")
            print(f"  ... and {total - 5} more" if total > 5 else "")
            return

        inserted = 0
        updated = 0
        from_nces = 0

        for i, (name, level, existing_addr, best_rating) in enumerate(schools_data):
            addr = existing_addr if existing_addr and not args.refresh else None
            city, state, zip_code = None, None, None
            lat, lng = None, None

            if not addr:
                nces = search_school_by_name(name, level, states=["NC", "SC"])
                if nces and nces.get("address"):
                    addr = nces["address"]
                    city = nces.get("city")
                    state = nces.get("state")
                    zip_code = nces.get("zip_code")
                    lat = nces.get("latitude")
                    lng = nces.get("longitude")
                    from_nces += 1
                if i < total - 1:
                    time.sleep(args.delay)
            else:
                zip_code = parse_zip_from_address(addr)

            row = db.execute(
                text("SELECT id FROM schools WHERE name = :name AND level = :level"),
                {"name": name, "level": level},
            ).fetchone()

            if row:
                db.execute(
                    text("""
                        UPDATE schools SET address = :addr, city = :city, state = :state,
                            zip_code = :zip, latitude = :lat, longitude = :lng, rating = :rating,
                            updated_at = now()
                        WHERE id = :id
                    """),
                    {
                        "addr": addr,
                        "city": city,
                        "state": state,
                        "zip": zip_code,
                        "lat": lat,
                        "lng": lng,
                        "rating": best_rating,
                        "id": row[0],
                    },
                )
                updated += 1
            else:
                db.execute(
                    text("""
                        INSERT INTO schools (name, level, address, city, state, zip_code, latitude, longitude, rating)
                        VALUES (:name, :level, :addr, :city, :state, :zip, :lat, :lng, :rating)
                    """),
                    {
                        "name": name,
                        "level": level,
                        "addr": addr,
                        "city": city,
                        "state": state,
                        "zip": zip_code,
                        "lat": lat,
                        "lng": lng,
                        "rating": best_rating,
                    },
                )
                inserted += 1

            if (i + 1) % 100 == 0:
                db.commit()
                print(f"  Progress: {i + 1}/{total} (inserted={inserted}, updated={updated})")

        db.commit()
        print(f"Done. Inserted {inserted}, updated {updated}, fetched from NCES {from_nces}")
        print("Next: python scripts/link_attendance_zones_to_schools.py")

    finally:
        db.close()


if __name__ == "__main__":
    main()

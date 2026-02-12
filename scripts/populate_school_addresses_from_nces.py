"""
Populate school_data school-level address columns from NCES EDGE API.

Fetches real addresses for each unique school (name + level) from the free NCES
public school database. Updates elementary_school_address, middle_school_address,
high_school_address. Also helps with:
- Exact zip match (parsed from address) for populate_total_schools
- Better zoning (address + lat/lng for point-in-polygon)

NCES has public schools only; charters may be included. Private schools won't match.

Usage:
    python scripts/populate_school_addresses_from_nces.py
    python scripts/populate_school_addresses_from_nces.py --limit 50
    python scripts/populate_school_addresses_from_nces.py --dry-run
    python scripts/populate_school_addresses_from_nces.py --refresh   # Re-fetch even if address exists
"""
import os
import sys
import time
from typing import Dict, List, Set, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text

from backend.database import SessionLocal
from backend.nces_client import search_school_by_name


def get_unique_schools(db, refresh: bool) -> List[Tuple[str, str]]:
    """Get unique (name, level) from school_data. If not refresh, skip those that already have address."""
    schools = []
    if refresh:
        sql_elem = """
            SELECT DISTINCT elementary_school_name, 'elementary'
            FROM school_data WHERE elementary_school_name IS NOT NULL AND elementary_school_rating IS NOT NULL
        """
        sql_mid = """
            SELECT DISTINCT middle_school_name, 'middle'
            FROM school_data WHERE middle_school_name IS NOT NULL AND middle_school_rating IS NOT NULL
        """
        sql_high = """
            SELECT DISTINCT high_school_name, 'high'
            FROM school_data WHERE high_school_name IS NOT NULL AND high_school_rating IS NOT NULL
        """
    else:
        sql_elem = """
            SELECT DISTINCT s.elementary_school_name, 'elementary'
            FROM school_data s
            WHERE s.elementary_school_name IS NOT NULL AND s.elementary_school_rating IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM school_data s2 WHERE s2.elementary_school_name = s.elementary_school_name
                AND s2.elementary_school_address IS NOT NULL AND TRIM(s2.elementary_school_address) <> ''
            )
        """
        sql_mid = """
            SELECT DISTINCT s.middle_school_name, 'middle'
            FROM school_data s
            WHERE s.middle_school_name IS NOT NULL AND s.middle_school_rating IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM school_data s2 WHERE s2.middle_school_name = s.middle_school_name
                AND s2.middle_school_address IS NOT NULL AND TRIM(s2.middle_school_address) <> ''
            )
        """
        sql_high = """
            SELECT DISTINCT s.high_school_name, 'high'
            FROM school_data s
            WHERE s.high_school_name IS NOT NULL AND s.high_school_rating IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM school_data s2 WHERE s2.high_school_name = s.high_school_name
                AND s2.high_school_address IS NOT NULL AND TRIM(s2.high_school_address) <> ''
            )
        """
    for sql in (sql_elem, sql_mid, sql_high):
        rows = db.execute(text(sql)).fetchall()
        schools.extend((str(r[0]).strip(), r[1]) for r in rows if r[0])
    # Dedupe and sort
    seen = set()
    out = []
    for name, level in sorted(schools, key=lambda x: (x[1], x[0])):
        k = (name, level)
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Populate school addresses from NCES")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--refresh", action="store_true", help="Re-fetch even if address already exists")
    parser.add_argument("--delay", type=float, default=0.15, help="Seconds between NCES requests (default 0.15)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        schools = get_unique_schools(db, args.refresh)
        if args.limit:
            schools = schools[: args.limit]

        total = len(schools)
        print(f"Found {total} unique schools to look up")

        if total == 0:
            print("Nothing to do (all schools already have addresses, or use --refresh)")
            return

        if args.dry_run:
            for name, level in schools[:10]:
                print(f"  Would lookup: {name} ({level})")
            print(f"  ... and {total - 10} more" if total > 10 else "")
            return

        matched = 0
        not_found = 0
        errors = 0

        for i, (name, level) in enumerate(schools):
            result = search_school_by_name(name, level, states=["NC", "SC"])
            if result and result.get("address"):
                addr = result["address"]
                if level == "elementary":
                    db.execute(
                        text("UPDATE school_data SET elementary_school_address = :addr WHERE elementary_school_name = :name"),
                        {"addr": addr, "name": name},
                    )
                elif level == "middle":
                    db.execute(
                        text("UPDATE school_data SET middle_school_address = :addr WHERE middle_school_name = :name"),
                        {"addr": addr, "name": name},
                    )
                else:
                    db.execute(
                        text("UPDATE school_data SET high_school_address = :addr WHERE high_school_name = :name"),
                        {"addr": addr, "name": name},
                    )
                matched += 1
                if (i + 1) % 25 == 0:
                    db.commit()
                    print(f"  Progress: {i + 1}/{total} ({matched} matched)")
            else:
                not_found += 1

            if i < total - 1 and args.delay > 0:
                time.sleep(args.delay)

        db.commit()
        print(f"Done. Matched: {matched}, Not found: {not_found}")
        print("Run 'python scripts/populate_total_schools.py' to refresh zip counts with new addresses.")

    finally:
        db.close()


if __name__ == "__main__":
    main()

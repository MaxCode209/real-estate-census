"""
Populate census_data.city using the free Zippopotam.us API (zip → place name).
No API key required. Results are cached locally so re-runs don't re-fetch.

Usage:
  python scripts/fetch_city_for_zips.py              # all zips in census_data
  python scripts/fetch_city_for_zips.py --limit 50   # first 50 (test)
  python scripts/fetch_city_for_zips.py --dry-run   # only fetch & cache, no DB update
  python scripts/fetch_city_for_zips.py --delay 0.5  # seconds between requests (default 0.25)

Requires: run migrate_add_city_to_census.py first so census_data has a 'city' column.
"""
import sys
import os
import json
import time
import argparse
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData

CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "zip_to_city_cache.json",
)
def _country_for_zip(zip_code):
    """Return Zippopotam country code: 'us' for mainland, 'pr' for Puerto Rico."""
    z = str(zip_code).strip()
    if z.startswith("006") or z.startswith("007") or z.startswith("009"):
        return "pr"
    return "us"


def load_cache():
    if os.path.isfile(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=0)


def fetch_city_for_zip(zip_code, cache, session):
    zip_code = str(zip_code).strip()
    if not zip_code or len(zip_code) != 5:
        return None
    if zip_code in cache:
        return cache[zip_code]
    try:
        country = _country_for_zip(zip_code)
        url = f"https://api.zippopotam.us/{country}/{zip_code}"
        r = session.get(url, timeout=10)
        if r.status_code != 200:
            cache[zip_code] = None
            return None
        data = r.json()
        places = data.get("places") or []
        if not places:
            cache[zip_code] = None
            return None
        place_name = places[0].get("place name") or places[0].get("place_name")
        cache[zip_code] = place_name
        return place_name
    except Exception:
        cache[zip_code] = None
        return None


def main():
    parser = argparse.ArgumentParser(description="Populate census_data.city from Zippopotam.us API")
    parser.add_argument("--limit", type=int, default=None, help="Max number of zips to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Only fetch and cache; do not update DB")
    parser.add_argument("--delay", type=float, default=0.25, help="Seconds between API requests (default: 0.25)")
    args = parser.parse_args()

    cache = load_cache()
    print(f"Cache has {len(cache)} zip->city entries (data/zip_to_city_cache.json)")

    db = SessionLocal()
    try:
        rows = db.query(CensusData.zip_code).distinct().order_by(CensusData.zip_code).all()
        zips = [r[0] for r in rows if r[0]]
    finally:
        db.close()

    if args.limit:
        zips = zips[: args.limit]
        print(f"Processing first {args.limit} zips (--limit)")
    else:
        print(f"Processing {len(zips)} zip codes from census_data")

    if args.dry_run:
        print("DRY RUN: will only fetch and cache, no DB updates")

    updated = 0
    skipped = 0
    http_session = requests.Session()
    db = SessionLocal() if not args.dry_run else None

    try:
        for i, zip_code in enumerate(zips):
            city = fetch_city_for_zip(zip_code, cache, http_session)
            if city:
                if not args.dry_run and db:
                    try:
                        db.query(CensusData).filter(CensusData.zip_code == zip_code).update(
                            {CensusData.city: city}, synchronize_session=False
                        )
                        db.commit()
                        updated += 1
                    except Exception as e:
                        db.rollback()
                        print(f"  Error updating {zip_code}: {e}")
                else:
                    updated += 1
            else:
                skipped += 1

            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(zips)} ... (updated {updated}, skipped {skipped})")
            time.sleep(args.delay)
    finally:
        if db:
            db.close()

    save_cache(cache)
    print(f"\nDone. Updated: {updated}, Skipped: {skipped}, Cache size: {len(cache)}")
    if args.dry_run:
        print("Re-run without --dry-run to apply updates to the database.")


if __name__ == "__main__":
    main()

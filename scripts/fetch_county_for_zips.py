"""
Populate census_data.county using Zippopotam (zip -> lat/lng) + FCC API (lat/lng -> county).
No API key required. Results are cached locally so re-runs don't re-fetch.

Usage:
  python scripts/fetch_county_for_zips.py              # all zips in census_data
  python scripts/fetch_county_for_zips.py --limit 50   # first 50 (test)
  python scripts/fetch_county_for_zips.py --dry-run    # only fetch and cache, no DB update
  python scripts/fetch_county_for_zips.py --delay 0.3  # seconds between requests (default 0.3)
  python scripts/fetch_county_for_zips.py --missing-only  # only zips that don't have a county yet
"""
import sys
import os
import json
import time
import argparse
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import or_, func
from backend.database import SessionLocal
from backend.models import CensusData

CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "zip_to_county_cache.json",
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


def fetch_county_for_zip(zip_code, cache, session):
    """Get county for zip: Zippopotam -> lat/lng, FCC -> county. Returns county name or None."""
    zip_code = str(zip_code).strip()
    if not zip_code or len(zip_code) != 5:
        return None
    if zip_code in cache:
        return cache[zip_code]
    try:
        # 1. Get lat/lng from Zippopotam
        country = _country_for_zip(zip_code)
        zippo_url = f"https://api.zippopotam.us/{country}/{zip_code}"
        r = session.get(zippo_url, timeout=10)
        if r.status_code != 200:
            cache[zip_code] = None
            return None
        data = r.json()
        places = data.get("places") or []
        if not places:
            cache[zip_code] = None
            return None
        lat = places[0].get("latitude") or places[0].get("lat")
        lng = places[0].get("longitude") or places[0].get("lng")
        if not lat or not lng:
            cache[zip_code] = None
            return None
        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except (TypeError, ValueError):
            cache[zip_code] = None
            return None

        # 2. Get county from FCC API (US only - PR zips may not have FCC data)
        if country != "us":
            cache[zip_code] = None
            return None
        fcc_url = f"https://geo.fcc.gov/api/census/block/find?latitude={lat_f}&longitude={lng_f}&format=json"
        r2 = session.get(fcc_url, timeout=10)
        if r2.status_code != 200:
            cache[zip_code] = None
            return None
        fcc = r2.json()
        county_obj = fcc.get("County") or {}
        county_name = county_obj.get("name")
        if county_name:
            # FCC returns "Mecklenburg County" - we can strip " County" if desired, or keep as-is
            cache[zip_code] = county_name
            return county_name
        cache[zip_code] = None
        return None
    except Exception:
        cache[zip_code] = None
        return None


def main():
    parser = argparse.ArgumentParser(description="Populate census_data.county from FCC API (via Zippopotam lat/lng)")
    parser.add_argument("--limit", type=int, default=None, help="Max number of zips to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Only fetch and cache; do not update DB")
    parser.add_argument("--delay", type=float, default=0.3, help="Seconds between API requests (default: 0.3)")
    parser.add_argument("--missing-only", action="store_true", help="Only process zips that don't have a county yet")
    args = parser.parse_args()

    cache = load_cache()
    print(f"Cache has {len(cache)} zip->county entries (data/zip_to_county_cache.json)")

    db = SessionLocal()
    try:
        q = db.query(CensusData.zip_code).distinct().order_by(CensusData.zip_code)
        if args.missing_only:
            q = q.filter(or_(CensusData.county.is_(None), func.trim(func.coalesce(CensusData.county, '')) == ''))
        rows = q.all()
        zips = [r[0] for r in rows if r[0]]
    finally:
        db.close()

    if args.limit:
        zips = zips[: args.limit]
        print(f"Processing first {args.limit} zips (--limit)")
    else:
        mode = "missing-only (no county yet)" if args.missing_only else "all"
        print(f"Processing {len(zips)} zip codes from census_data ({mode})")

    if args.dry_run:
        print("DRY RUN: will only fetch and cache, no DB updates")

    updated = 0
    skipped = 0
    http_session = requests.Session()
    db = SessionLocal() if not args.dry_run else None

    try:
        for i, zip_code in enumerate(zips):
            county = fetch_county_for_zip(zip_code, cache, http_session)
            if county:
                if not args.dry_run and db:
                    try:
                        db.query(CensusData).filter(CensusData.zip_code == zip_code).update(
                            {CensusData.county: county}, synchronize_session=False
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
                save_cache(cache)
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

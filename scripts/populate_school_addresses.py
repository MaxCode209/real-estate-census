"""
Populate school_data.address and school_data.zip_code via reverse geocoding.

Uses nearest zip centroid (free, instant) - no external API.
Optionally uses Nominatim (OpenStreetMap) for full address when --use-nominatim.

Nearest-centroid approach:
- Looks up zip from zip_code_centroids for each (lat, lng)
- Sets address to "Area in ZIP {zip}" (placeholder; accurate zip for counting)

After running, populate_total_schools will use row zip when assigning schools
to zips for more accurate elementary_schools/middle_schools/high_schools counts.

Usage:
    python scripts/populate_school_addresses.py          # Fast: nearest centroid only
    python scripts/populate_school_addresses.py --use-nominatim   # Slower: full address (1 req/sec)
    python scripts/populate_school_addresses.py --limit 50        # Test with 50 rows
    python scripts/populate_school_addresses.py --dry-run         # Preview only
"""
import os
import sys
import time
from typing import List, Optional, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text

from backend.database import SessionLocal

# For optional Nominatim (requires custom User-Agent per OSM policy)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "RealEstateCensus/1.0 (https://github.com/MaxCode209/real-estate-census)"


def nearest_zip(lat: float, lng: float, centroids: List[Tuple[str, float, float]]) -> Optional[str]:
    """Return zip with nearest centroid to (lat, lng)."""
    if not centroids:
        return None
    best_zip, best_dist = None, float("inf")
    for zc, clat, clng in centroids:
        d = (lat - clat) ** 2 + (lng - clng) ** 2
        if d < best_dist:
            best_dist = d
            best_zip = zc
    return best_zip


def reverse_geocode_nominatim(lat: float, lng: float) -> Tuple[Optional[str], Optional[str]]:
    """Reverse geocode via Nominatim. Returns (address, zip_code). Rate limit: 1/sec."""
    try:
        import requests
        r = requests.get(
            NOMINATIM_URL,
            params={"lat": lat, "lon": lng, "format": "json", "addressdetails": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        addr = data.get("display_name")
        addr_dict = data.get("address") or {}
        zip_code = addr_dict.get("postcode") or addr_dict.get("zipcode")
        import re
        if not zip_code and addr:
            m = re.search(r"\b(\d{5})(?:-\d{4})?\b", str(addr))
            zip_code = m.group(1) if m else None
        return (
            str(addr).strip() if addr else None,
            str(zip_code).strip() if zip_code else None,
        )
    except Exception as e:
        print(f"  [WARN] Nominatim failed for ({lat},{lng}): {e}")
        return (None, None)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Populate school_data address and zip_code")
    parser.add_argument("--limit", type=int, default=None, help="Max rows to process")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no DB writes")
    parser.add_argument("--use-nominatim", action="store_true",
                        help="Use Nominatim for full address (slow, 1 req/sec). Default uses nearest centroid.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        centroids = []
        if not args.use_nominatim:
            # Load zip centroids for nearest-centroid lookup (NC/SC bounds)
            centroid_sql = """
                SELECT zip_code, latitude, longitude
                FROM zip_code_centroids
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                  AND latitude BETWEEN 32 AND 38 AND longitude BETWEEN -85 AND -74
            """
            rows_c = db.execute(text(centroid_sql)).fetchall()
            centroids = [(r[0], float(r[1]), float(r[2])) for r in rows_c]
            print(f"Loaded {len(centroids)} zip centroids (nearest-centroid mode)")

        sql = """
            SELECT id, latitude, longitude
            FROM school_data
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
              AND (address IS NULL OR zip_code IS NULL)
            ORDER BY id
        """
        if args.limit:
            sql += f" LIMIT {args.limit}"
        rows = db.execute(text(sql)).fetchall()
        total = len(rows)
        print(f"Found {total} rows needing address/zip")

        if total == 0:
            print("Nothing to do.")
            return

        if args.dry_run:
            print(f"[DRY RUN] Would process {total} rows")
            for i, row in enumerate(rows[:3]):
                print(f"  Sample: id={row[0]}, lat={row[1]}, lng={row[2]}")
            return

        updated = 0
        failed = 0
        for i, row in enumerate(rows):
            row_id, lat, lng = row[0], float(row[1]), float(row[2])
            if args.use_nominatim:
                addr, zip_code = reverse_geocode_nominatim(lat, lng)
                if i < total - 1:
                    time.sleep(1.0)
            else:
                zip_code = nearest_zip(lat, lng, centroids) if centroids else None
                addr = f"Area in ZIP {zip_code}" if zip_code else None

            if addr or zip_code:
                db.execute(
                    text("""
                        UPDATE school_data
                        SET address = :addr, zip_code = :zip
                        WHERE id = :id
                    """),
                    {"addr": addr, "zip": zip_code, "id": row_id},
                )
                updated += 1
                if (i + 1) % 200 == 0:
                    db.commit()
                    print(f"  Progress: {i + 1}/{total} ({updated} updated)")
            else:
                failed += 1

        db.commit()
        print(f"Done. Updated {updated}, failed {failed}")

    finally:
        db.close()


if __name__ == "__main__":
    main()

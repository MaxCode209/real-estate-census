"""
Populate census_data school columns: counts and average ratings.

Columns: total_schools, elementary_schools, middle_schools, high_schools,
         average_school_rating, elementary_school_rating, middle_school_rating, high_school_rating, top_school_rating.

Uses school_data: each row has lat/lng, school names, and ratings (1-10).
Assigns each unique school (by name + level) to the zip with nearest centroid.

Usage:
    python scripts/populate_total_schools.py
    python scripts/populate_total_schools.py --dry-run
"""
import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text

from backend.database import SessionLocal


def haversine_approx(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Approximate distance squared (relative); no sqrt needed for min comparison."""
    dlat = lat1 - lat2
    dlng = lng1 - lng2
    return dlat * dlat + dlng * dlng


def nearest_zip(lat: float, lng: float, centroids: List[Tuple[str, float, float]]) -> Optional[str]:
    """Return zip_code with nearest centroid to (lat, lng)."""
    if not centroids:
        return None
    best_zip, best_dist = None, float("inf")
    for zc, clat, clng in centroids:
        d = haversine_approx(lat, lng, clat, clng)
        if d < best_dist:
            best_dist = d
            best_zip = zc
    return best_zip


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Populate census_data.total_schools")
    parser.add_argument("--dry-run", action="store_true", help="Compute but do not write to DB")
    parser.add_argument("--bounds", action="store_true", default=True,
                        help="Restrict centroids to NC/SC bounding box (default: True)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        # 1. Load zip centroids (optionally restrict to NC/SC area for speed)
        centroid_sql = """
            SELECT zip_code, latitude, longitude
            FROM zip_code_centroids
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        if args.bounds:
            centroid_sql += " AND latitude BETWEEN 32 AND 38 AND longitude BETWEEN -85 AND -74"
        centroid_sql += " ORDER BY zip_code"
        rows = db.execute(text(centroid_sql)).fetchall()
        centroids = [(r[0], float(r[1]), float(r[2])) for r in rows]
        print(f"Loaded {len(centroids)} zip centroids")

        # 2. Load school_data: unique (name, level) with first-seen lat/lng and rating
        school_sql = """
            SELECT id, latitude, longitude,
                   elementary_school_name, elementary_school_rating,
                   middle_school_name, middle_school_rating,
                   high_school_name, high_school_rating
            FROM school_data
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
              AND (elementary_school_name IS NOT NULL OR middle_school_name IS NOT NULL OR high_school_name IS NOT NULL)
        """
        rows = db.execute(text(school_sql)).fetchall()

        # For each unique (name, level), keep first (lat, lng, rating) we see
        school_to_data: Dict[Tuple[str, str], Tuple[float, float, float]] = {}
        for row in rows:
            lat_f, lng_f = float(row[1]), float(row[2])
            for name, rating, level in [
                (row[3], row[4], "elementary"),
                (row[5], row[6], "middle"),
                (row[7], row[8], "high"),
            ]:
                if name and (n := str(name).strip()) and rating is not None:
                    try:
                        r = float(rating)
                        if 0 <= r <= 10:
                            key = (n, level)
                            if key not in school_to_data:
                                school_to_data[key] = (lat_f, lng_f, r)
                    except (TypeError, ValueError):
                        pass

        print(f"Found {len(school_to_data)} unique schools with ratings")

        # 3. Assign each school to nearest zip; count and collect ratings per zip by level
        zip_elem: Dict[str, Set[str]] = defaultdict(set)
        zip_mid: Dict[str, Set[str]] = defaultdict(set)
        zip_high: Dict[str, Set[str]] = defaultdict(set)
        zip_elem_ratings: Dict[str, List[float]] = defaultdict(list)
        zip_mid_ratings: Dict[str, List[float]] = defaultdict(list)
        zip_high_ratings: Dict[str, List[float]] = defaultdict(list)
        for (school_name, level), (lat, lng, rating) in school_to_data.items():
            z = nearest_zip(lat, lng, centroids)
            if z:
                if level == "elementary":
                    zip_elem[z].add(school_name)
                    zip_elem_ratings[z].append(rating)
                elif level == "middle":
                    zip_mid[z].add(school_name)
                    zip_mid_ratings[z].append(rating)
                else:
                    zip_high[z].add(school_name)
                    zip_high_ratings[z].append(rating)

        # Build counts and average ratings per zip
        all_zips = set(zip_elem) | set(zip_mid) | set(zip_high)
        zip_counts: Dict[str, Tuple[int, int, int, int, Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]] = {}
        for z in all_zips:
            e, m, h = len(zip_elem[z]), len(zip_mid[z]), len(zip_high[z])
            tot = e + m + h
            all_ratings = zip_elem_ratings[z] + zip_mid_ratings[z] + zip_high_ratings[z]
            avg_elem = sum(zip_elem_ratings[z]) / len(zip_elem_ratings[z]) if zip_elem_ratings[z] else None
            avg_mid = sum(zip_mid_ratings[z]) / len(zip_mid_ratings[z]) if zip_mid_ratings[z] else None
            avg_high = sum(zip_high_ratings[z]) / len(zip_high_ratings[z]) if zip_high_ratings[z] else None
            avg_all = sum(all_ratings) / len(all_ratings) if all_ratings else None
            top = max(all_ratings) if all_ratings else None
            zip_counts[z] = (tot, e, m, h, avg_all, avg_elem, avg_mid, avg_high, top)

        print(f"Assigned schools to {len(zip_counts)} zips; total schools placed: {sum(c[0] for c in zip_counts.values())}")

        if args.dry_run:
            sample = sorted(zip_counts.items(), key=lambda x: -x[1][0])[:10]
            print("Top 10 zips (dry run): total | elem | mid | high | avg | avg_elem | avg_mid | avg_high | top")
            for z, (tot, e, m, h, avg_all, avg_e, avg_m, avg_h, top) in sample:
                ae = f"{avg_e:.1f}" if avg_e is not None else "-"
                am = f"{avg_m:.1f}" if avg_m is not None else "-"
                ah = f"{avg_h:.1f}" if avg_h is not None else "-"
                aa = f"{avg_all:.1f}" if avg_all is not None else "-"
                tp = f"{top:.1f}" if top is not None else "-"
                print(f"  {z}: {tot} | elem={e} mid={m} high={h} | avg={aa} elem={ae} mid={am} high={ah} top={tp}")
            return

        # 4a. Check if level-specific rating columns exist
        _have_level_ratings = False
        col_check = db.execute(text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='census_data' AND column_name='average_elementary_school_rating'
        """)).fetchone()
        if col_check:
            _have_level_ratings = True
        else:
            print("Note: Level-specific rating columns not found. Run migration 20260213000000_add_school_rating_columns.sql in Supabase SQL Editor, then re-run this script.")

        # 4b. Reset all census_data school columns to 0 / NULL
        reset_sql = """
            UPDATE census_data
            SET total_schools = 0, elementary_schools = 0, middle_schools = 0, high_schools = 0,
                average_school_rating = NULL, top_school_rating = NULL
        """
        if _have_level_ratings:
            reset_sql = """
                UPDATE census_data
                SET total_schools = 0, elementary_schools = 0, middle_schools = 0, high_schools = 0,
                    average_school_rating = NULL, top_school_rating = NULL,
                    average_elementary_school_rating = NULL, average_middle_school_rating = NULL,
                    average_high_school_rating = NULL
            """
        r = db.execute(text(reset_sql))
        db.commit()
        print(f"Reset school columns for {r.rowcount} rows")

        # 5. Update census_data school columns for zips that have schools
        updated = 0
        if _have_level_ratings:
            for zip_code, (total, elem, mid, high, avg_all, avg_e, avg_m, avg_h, top) in zip_counts.items():
                r = db.execute(
                    text("""
                        UPDATE census_data
                        SET total_schools = :tot, elementary_schools = :elem, middle_schools = :mid, high_schools = :high,
                            average_school_rating = :avg_all, top_school_rating = :top_r,
                            average_elementary_school_rating = :avg_e, average_middle_school_rating = :avg_m,
                            average_high_school_rating = :avg_h
                        WHERE zip_code = :zip
                    """),
                    {
                        "tot": total, "elem": elem, "mid": mid, "high": high,
                        "avg_all": avg_all, "avg_e": avg_e, "avg_m": avg_m, "avg_h": avg_h, "top_r": top,
                        "zip": zip_code,
                    },
                )
                if r.rowcount > 0:
                    updated += 1
        else:
            for zip_code, (total, elem, mid, high, avg_all, avg_e, avg_m, avg_h, top) in zip_counts.items():
                r = db.execute(
                    text("""
                        UPDATE census_data
                        SET total_schools = :tot, elementary_schools = :elem, middle_schools = :mid, high_schools = :high,
                            average_school_rating = :avg_all, top_school_rating = :top_r
                        WHERE zip_code = :zip
                    """),
                    {"tot": total, "elem": elem, "mid": mid, "high": high, "avg_all": avg_all, "top_r": top, "zip": zip_code},
                )
                if r.rowcount > 0:
                    updated += 1
            print("Note: Run migration 20260213000000_add_school_rating_columns.sql for elem/mid/high averages")
        db.commit()
        print(f"Updated school counts and ratings for {updated} zip codes")

    finally:
        db.close()


if __name__ == "__main__":
    main()

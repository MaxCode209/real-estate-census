"""
Link attendance_zones to schools table by matching school_name + school_level.

Sets canonical_school_id when we find a schools row that matches (fuzzy).
Run after populate_schools_table.py.

Usage:
    python scripts/link_attendance_zones_to_schools.py
    python scripts/link_attendance_zones_to_schools.py --dry-run
"""
import os
import sys
from difflib import SequenceMatcher

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text

from backend.database import SessionLocal


def normalize(name: str) -> str:
    """Lowercase, strip, collapse spaces."""
    if not name:
        return ""
    return " ".join(str(name).lower().strip().split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        schools = db.execute(text("SELECT id, name, level FROM schools")).fetchall()
        school_lookup = {}  # (normalize(name), level) -> [(id, name), ...]
        for sid, name, level in schools:
            key = (normalize(name), (level or "").lower())
            if key not in school_lookup:
                school_lookup[key] = []
            school_lookup[key].append((sid, name))

        zones = db.execute(
            text("SELECT id, school_name, school_level FROM attendance_zones WHERE state IN ('NC', 'SC')")
        ).fetchall()

        total_zones = len(zones)
        print(f"Linking {total_zones} zones to {len(schools)} schools...")

        matched = 0
        unmatched = 0
        for i, (zid, z_name, z_level) in enumerate(zones):
            if (i + 1) % 500 == 0:
                print(f"  Progress: {i + 1}/{total_zones} (matched={matched})")
            z_level = (z_level or "").lower()
            key = (normalize(z_name), z_level)
            candidates = school_lookup.get(key)
            if not candidates:
                # Try fuzzy: same level, similar name
                best = None
                best_score = 0.0
                for (s_name, s_level), s_list in school_lookup.items():
                    if s_level != z_level:
                        continue
                    for sid, _ in s_list:
                        score = similarity(z_name, s_name)
                        if score > best_score and score >= 0.8:
                            best_score = score
                            best = sid
                if best:
                    candidates = [(best, "")]
            if candidates:
                school_id = candidates[0][0]
                if not args.dry_run:
                    db.execute(
                        text("UPDATE attendance_zones SET canonical_school_id = :sid WHERE id = :zid"),
                        {"sid": school_id, "zid": zid},
                    )
                matched += 1
            else:
                unmatched += 1

        if not args.dry_run:
            db.commit()
        print(f"Matched: {matched}, Unmatched: {unmatched}")

    finally:
        db.close()


if __name__ == "__main__":
    main()

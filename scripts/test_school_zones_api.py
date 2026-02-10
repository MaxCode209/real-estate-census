"""
Diagnostic: simulate /api/zips/<zip>/school-zones and print debug.
Run: python scripts/test_school_zones_api.py [zip_code]
Example: python scripts/test_school_zones_api.py 28202
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from backend.database import SessionLocal
from backend.models import AttendanceZone
from sqlalchemy import or_
from backend.zone_utils import (
    load_zip_polygon,
    zones_intersecting_zip_diagnostic,
    zone_boundary_to_wgs84,
    _boundary_to_shapely_wgs84,
    _coords_look_projected,
)

def get_first_coord(coords):
    while coords and isinstance(coords, list) and len(coords) > 0:
        if isinstance(coords[0], (int, float)):
            return coords[0], coords[1] if len(coords) > 1 else None
        coords = coords[0]
    return None

def main():
    zip_code = (sys.argv[1] if len(sys.argv) > 1 else None) or "28202"
    print("=" * 60)
    print("School Zones API Diagnostic")
    print("=" * 60)
    print(f"Zip: {zip_code}")

    # 1) Zip boundary
    zip_polygon = load_zip_polygon(zip_code)
    if zip_polygon is None:
        print("\n[FAIL] No zip boundary file: data/zip_boundaries/{}.geojson".format(zip_code))
        # List a few available zips
        bp = Path("data/zip_boundaries")
        if bp.exists():
            files = list(bp.glob("*.geojson"))[:5]
            print("  Sample available zips:", [f.stem for f in files])
        return 1
    print("\n[OK] Zip boundary loaded (WGS84)")

    # 2) Zones in DB (limit for fast diagnostic; API uses all)
    db = SessionLocal()
    try:
        zones = db.query(AttendanceZone).filter(
            or_(AttendanceZone.state == "NC", AttendanceZone.state == "SC")
        ).limit(2000).all()
        zones_list = [z.to_dict() for z in zones]
        total_nc_sc = db.query(AttendanceZone).filter(
            or_(AttendanceZone.state == "NC", AttendanceZone.state == "SC")
        ).count()
    finally:
        db.close()

    if not zones_list:
        print("[FAIL] No NC/SC attendance zones in database. Run: python scripts/import_nces_zones.py")
        return 1
    print(f"[OK] NC/SC zones in DB: {total_nc_sc} (testing with {len(zones_list)} sample)")

    # 3) Sample zone: raw boundary format and WGS84 conversion
    sample = zones_list[0]
    raw = sample.get("zone_boundary")
    state = (sample.get("state") or "").strip().upper()
    print(f"\nSample zone: {sample.get('school_name')} ({sample.get('school_level')}, {sample.get('state')})")
    if isinstance(raw, dict):
        geom = raw
    else:
        try:
            geom = json.loads(raw) if isinstance(raw, str) else raw
        except Exception as e:
            print(f"  [ERROR] zone_boundary parse failed: {e}")
            geom = None
    if geom:
        gtype = geom.get("type") if isinstance(geom, dict) else None
        coords = geom.get("coordinates") if isinstance(geom, dict) else None
        first = get_first_coord(coords) if coords else None
        print(f"  Raw geometry type: {gtype}, first coord: {first}")
        if first:
            looks_projected = _coords_look_projected(coords)
            print(f"  Coords look projected (need transform): {looks_projected}")
        wgs84 = zone_boundary_to_wgs84(raw, state_abbr=state)
        if wgs84:
            first_w = get_first_coord(wgs84.get("coordinates"))
            print(f"  After zone_boundary_to_wgs84: type={wgs84.get('type')}, first coord: {first_w}")
        else:
            print("  [ERROR] zone_boundary_to_wgs84 returned None")
        shapely_geom = _boundary_to_shapely_wgs84(sample)
        print(f"  _boundary_to_shapely_wgs84: {'OK' if shapely_geom else 'None'}")

    # 4) Full pipeline: intersecting count
    intersecting, diag = zones_intersecting_zip_diagnostic(zip_polygon, zones_list)
    print("\n" + "-" * 60)
    print("Diagnostic (same as API response when no districts):")
    print(json.dumps(diag, indent=2))
    print("-" * 60)
    print(f"Districts that would be returned: {len(intersecting)} zones -> grouped by district")

    if diag["zones_with_geometry"] == 0:
        print("\n[ISSUE] No zones have valid geometry after WGS84 conversion. Check zone_boundary format and CRS.")
    elif diag["intersecting_count"] == 0:
        print("\n[ISSUE] All zones have geometry but none intersect this zip. Possible CRS mismatch or zip outside NC/SC.")
    else:
        print("\n[OK] Pipeline would return districts. If UI still shows 'No districts', check frontend/network.")

    return 0

if __name__ == "__main__":
    sys.exit(main())

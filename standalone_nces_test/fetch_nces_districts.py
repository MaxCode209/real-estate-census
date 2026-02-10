"""
Standalone test: fetch NCES district geometry (no TIGER, no app routes).
Run from project root: python standalone_nces_test/fetch_nces_districts.py [zip]
Output: standalone_nces_test/nces_districts_<zip>.geojson and nces_only_map.html
Open nces_only_map.html in a browser to see ONLY NCES district boundaries (no zip/TIGER).
"""
import sys
import os
import json

# Run from project root; add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from pathlib import Path
from backend.database import SessionLocal
from backend.models import AttendanceZone
from sqlalchemy import or_
from backend.zone_utils import (
    load_zip_polygon,
    zones_intersecting_zip_diagnostic,
    group_zones_by_district,
    district_geometry_in_zip,
)

OUT_DIR = Path(__file__).resolve().parent
ZIP_DEFAULT = "28202"
COLORS = ["#E91E63", "#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#00BCD4", "#F44336", "#8BC34A"]


def main():
    zip_code = (sys.argv[1] if len(sys.argv) > 1 else None) or ZIP_DEFAULT
    zip_code = zip_code.strip()
    if not zip_code.isdigit() or len(zip_code) != 5:
        print("Usage: python standalone_nces_test/fetch_nces_districts.py [zip_code]")
        print("Example: python standalone_nces_test/fetch_nces_districts.py 28202")
        return 1

    print("=" * 60)
    print("Standalone NCES test (no TIGER, no app)")
    print("=" * 60)
    print(f"Zip: {zip_code}")

    zip_polygon = load_zip_polygon(zip_code)
    if zip_polygon is None:
        print("[FAIL] No zip boundary: data/zip_boundaries/{}.geojson".format(zip_code))
        return 1
    print("[OK] Zip boundary loaded (used only for intersection; not drawn)")

    db = SessionLocal()
    try:
        zones = db.query(AttendanceZone).filter(
            or_(AttendanceZone.state == "NC", AttendanceZone.state == "SC")
        ).all()
        zones_list = [z.to_dict() for z in zones]
    finally:
        db.close()

    if not zones_list:
        print("[FAIL] No NC/SC zones in DB. Run: python scripts/import_nces_zones.py")
        return 1
    print(f"[OK] NC/SC zones in DB: {len(zones_list)}")

    intersecting, diag = zones_intersecting_zip_diagnostic(zip_polygon, zones_list)
    print(f"  Diagnostic: {diag}")

    if not intersecting:
        print("[FAIL] No zones intersect this zip.")
        return 1

    grouped = group_zones_by_district(intersecting)
    features = []
    for i, grp in enumerate(grouped):
        geom = district_geometry_in_zip(zip_polygon, grp["zones"])
        if not geom:
            continue
        color = COLORS[i % len(COLORS)]
        features.append({
            "type": "Feature",
            "properties": {
                "district_name": grp.get("district_name") or "Unknown",
                "district_id": grp.get("district_id") or "",
                "color": color,
            },
            "geometry": geom,
        })

    if not features:
        print("[FAIL] No district geometry produced.")
        return 1

    fc = {"type": "FeatureCollection", "features": features}
    geojson_path = OUT_DIR / f"nces_districts_{zip_code}.geojson"
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(fc, f, indent=2)
    print(f"[OK] Wrote {geojson_path} ({len(features)} district(s))")

    # Generate self-contained HTML with embedded GeoJSON (no server needed)
    html_path = OUT_DIR / "nces_only_map.html"
    geojson_escaped = json.dumps(fc).replace("</", "<\\/")
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>NCES districts only (no TIGER)</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body { margin: 0; font-family: sans-serif; }
    #map { width: 100vw; height: 100vh; }
    #title { position: absolute; top: 10px; left: 10px; z-index: 1000;
             background: #fff; padding: 8px 12px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.3); }
  </style>
</head>
<body>
  <div id="title"><strong>NCES districts only</strong> (no TIGER, no zip boundary) &ndash; Zip """ + zip_code + """</div>
  <div id="map"></div>
  <script>
    var geojson = """ + geojson_escaped + """;
    var map = L.map('map').setView([35.2, -80.8], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OSM' }).addTo(map);
    var layer = L.geoJSON(geojson, {
      style: function(f) { return { color: f.properties.color || '#E91E63', weight: 3, fillOpacity: 0.35 }; },
      onEachFeature: function(f, layer) {
        layer.bindPopup('<b>' + (f.properties.district_name || 'District') + '</b>');
      }
    }).addTo(map);
    if (layer.getBounds && layer.getBounds().isValid()) map.fitBounds(layer.getBounds(), { padding: [40, 40] });
  </script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Wrote {html_path}")
    print("")
    print("Open in browser: standalone_nces_test/nces_only_map.html")
    print("(If opened as file://, some browsers allow it. Otherwise: python -m http.server 8888 from project root, then http://localhost:8888/standalone_nces_test/nces_only_map.html)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

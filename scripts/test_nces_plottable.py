"""
Standalone test: NCES attendance zone data — validate geometry and that coordinates
can be plotted on an open-source map. Does NOT modify any app code or app state.

Run:
  python scripts/test_nces_plottable.py
  python scripts/test_nces_plottable.py 28202   # optional: use this zip for district-in-zip test

Outputs:
  - Console report: zone counts, WGS84 vs projected, zip-intersection check.
  - scripts/output/test_nces_map.html: Leaflet + OSM map with sample zones (and
    optional zip + district boundaries). Open in a browser to verify utility.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

# Read-only imports from the app
from backend.database import SessionLocal
from backend.models import AttendanceZone
from sqlalchemy import or_

# Use zone_utils only for geometry helpers (read-only)
from backend.zone_utils import (
    load_zip_polygon,
    zones_intersecting_zip,
    group_zones_by_district,
    district_geometry_in_zip,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_HTML = OUTPUT_DIR / "test_nces_map.html"

# WGS84 bounds
LON_MIN, LON_MAX = -180, 180
LAT_MIN, LAT_MAX = -90, 90


def get_first_coord(geometry):
    """Get first [lon, lat] from GeoJSON coordinates (Polygon or MultiPolygon)."""
    coords = geometry.get("coordinates") or []
    while coords and isinstance(coords[0], list):
        coords = coords[0]
    if coords and len(coords) >= 2 and isinstance(coords[0], (int, float)):
        return float(coords[0]), float(coords[1])
    return None


def coords_in_wgs84(geometry):
    """Check if geometry coordinates look like WGS84 (lon/lat in range)."""
    first = get_first_coord(geometry)
    if first is None:
        return None
    lon, lat = first
    if LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX:
        return True
    return False


def geometry_to_geojson_feature(geometry_dict, props=None):
    """Ensure we have a GeoJSON Feature for Leaflet (type, geometry, properties)."""
    if geometry_dict.get("type") == "Feature":
        return geometry_dict
    return {"type": "Feature", "geometry": geometry_dict, "properties": props or {}}


def collect_geojson_for_leaflet(zone_boundary):
    """Parse zone_boundary (str or dict) to GeoJSON geometry; return None if invalid."""
    try:
        data = json.loads(zone_boundary) if isinstance(zone_boundary, str) else zone_boundary
    except Exception:
        return None
    if data.get("type") == "Feature":
        geom = data.get("geometry")
    elif data.get("type") == "FeatureCollection":
        feats = data.get("features", [])
        if not feats:
            return None
        geom = feats[0].get("geometry") if isinstance(feats[0], dict) else None
    else:
        geom = data
    if not geom or geom.get("type") not in ("Polygon", "MultiPolygon"):
        return None
    return geom


def run_nces_plottable_test(sample_zip=None):
    """Run validation and produce report + HTML map."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    db = SessionLocal()
    try:
        # Query all for count, then sample for validation (keeps test fast under load)
        total_in_db = db.query(AttendanceZone).filter(
            or_(AttendanceZone.state == "NC", AttendanceZone.state == "SC")
        ).count()
        zones = db.query(AttendanceZone).filter(
            or_(AttendanceZone.state == "NC", AttendanceZone.state == "SC")
        ).limit(2000).all()
    finally:
        db.close()

    total = len(zones)
    print("=" * 60)
    print("NCES Attendance Zone Data – Plottable Test")
    print("=" * 60)
    print(f"Total NC/SC zones in DB: {total_in_db} (validated sample: {total})")

    if total == 0:
        print("\nNo zones found. Import NCES data first (e.g. scripts/import_nces_zones.py).")
        _write_html_no_data()
        return

    # Validate each zone's geometry
    valid_wgs84 = 0
    valid_projected = 0
    parse_error = 0
    no_geom = 0
    sample_for_map = []  # list of (zone, geom_dict) for HTML

    for zone in zones:
        raw = zone.zone_boundary
        if not raw:
            no_geom += 1
            continue
        geom = collect_geojson_for_leaflet(raw)
        if geom is None:
            parse_error += 1
            continue
        in_wgs84 = coords_in_wgs84(geom)
        if in_wgs84 is True:
            valid_wgs84 += 1
            if len(sample_for_map) < 12:  # keep a few for map
                sample_for_map.append((zone, geom))
        elif in_wgs84 is False:
            valid_projected += 1
        else:
            parse_error += 1

    print(f"  Valid WGS84 (plottable on OSM/Leaflet): {valid_wgs84}")
    print(f"  Projected / other CRS:                 {valid_projected}")
    print(f"  Parse error / no coords:                {parse_error}")
    print(f"  No boundary:                            {no_geom}")

    # Zip + district slice test (optional)
    zip_ok = False
    district_geometries = []
    test_zip = sample_zip

    if not test_zip:
        # Pick first zip that has a boundary file
        boundaries_dir = Path("data/zip_boundaries")
        if boundaries_dir.exists():
            geojson_files = list(boundaries_dir.glob("*.geojson"))
            if geojson_files:
                test_zip = geojson_files[0].stem

    if test_zip:
        zip_polygon = load_zip_polygon(test_zip)
        if zip_polygon is not None:
            zones_list = [z.to_dict() for z in zones]
            intersecting = zones_intersecting_zip(zip_polygon, zones_list)
            grouped = group_zones_by_district(intersecting)
            print(f"\nZip code: {test_zip}")
            print(f"  Zones intersecting zip: {len(intersecting)}")
            print(f"  Districts in zip:       {len(grouped)}")
            zip_ok = True
            for grp in grouped[:6]:  # up to 6 districts for map
                geom_dict = district_geometry_in_zip(zip_polygon, grp["zones"])
                if geom_dict and coords_in_wgs84(geom_dict):
                    district_geometries.append((grp.get("district_name") or "District", geom_dict))
        else:
            print(f"\nZip {test_zip}: no boundary file in data/zip_boundaries/ (skip district slice test).")
    else:
        print("\nNo zip boundary dir or no data/zip_boundaries/*.geojson (skip district slice test).")

    # Build HTML map (Leaflet + OSM)
    features = []
    for zone, geom in sample_for_map:
        features.append(geometry_to_geojson_feature(geom, {"name": (zone.school_name or "")[:60], "level": zone.school_level or ""}))

    # Add zip boundary if we have it (from file)
    zip_geojson = None
    if test_zip:
        zip_path = Path("data/zip_boundaries") / f"{test_zip}.geojson"
        if zip_path.exists():
            try:
                with open(zip_path, "r", encoding="utf-8") as f:
                    zip_geojson = json.load(f)
            except Exception:
                pass

    # Add district slices
    for name, geom_dict in district_geometries:
        features.append(geometry_to_geojson_feature(geom_dict, {"name": f"District: {name}"}))

    html = _build_leaflet_html(
        zone_features=features,
        zip_geojson=zip_geojson,
        test_zip=test_zip,
        valid_wgs84=valid_wgs84,
        total=total,
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    # Write a short README in output dir
    readme = OUTPUT_DIR / "README.txt"
    with open(readme, "w", encoding="utf-8") as f:
        f.write("test_nces_map.html = output of scripts/test_nces_plottable.py\n")
        f.write("Open in a browser to verify NCES zone boundaries plot on Leaflet + OpenStreetMap.\n")

    print("\n" + "=" * 60)
    print("Output")
    print("=" * 60)
    print(f"  Open in browser: {OUTPUT_HTML}")
    print("  Use this to confirm NCES boundaries plot correctly on an open-source map (Leaflet + OSM).")
    if zip_ok and district_geometries:
        print("  Map includes sample zone boundaries and district-within-zip slices for zip:", test_zip)
    else:
        print("  Map includes sample zone boundaries only (no zip/district slice; add data/zip_boundaries/<zip>.geojson for that).")


def _write_html_no_data():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    html = _build_leaflet_html(zone_features=[], zip_geojson=None, test_zip=None, valid_wgs84=0, total=0)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Wrote {OUTPUT_HTML} (no data to show).")


def _build_leaflet_html(zone_features, zip_geojson, test_zip, valid_wgs84, total):
    """Build a self-contained HTML file with Leaflet + OSM."""
    zone_json = json.dumps({"type": "FeatureCollection", "features": zone_features})
    zip_json = json.dumps(zip_geojson) if zip_geojson else "null"
    title = "NCES Zones Plottable Test"
    if test_zip:
        title += f" (sample zip: {test_zip})"
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
  <div style="padding: 10px; font-family: sans-serif;">
    <h1>{title}</h1>
    <p>Zones in WGS84: <strong>{valid_wgs84}</strong> / {total}. District boundaries within a zip are shown if available.</p>
  </div>
  <div id="map" style="height: 600px;"></div>
  <script>
    var map = L.map('map').setView([35.5, -79.0], 8);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }}).addTo(map);

    var zoneData = {zone_json};
    var zipData = {zip_json};

    var colors = ['#4A90D9', '#50C878', '#E6A23C', '#E07070', '#9B59B6', '#1ABC9C', '#E67E22', '#3498DB'];
    if (zoneData.features && zoneData.features.length) {{
      zoneData.features.forEach(function(f, i) {{
        var style = {{ color: colors[i % colors.length], weight: 2, fillOpacity: 0.2 }};
        var popupText = (f.properties && f.properties.name) || 'Zone ' + (i+1);
        var layer = L.geoJSON(f, {{
          style: style,
          onEachFeature: function(lyr, feat) {{ lyr.bindPopup(popupText); }}
        }});
        layer.addTo(map);
      }});
    }}
    if (zipData && zipData.features && zipData.features.length) {{
      var zipLayer = L.geoJSON(zipData, {{ color: '#333', weight: 3, fillOpacity: 0 }});
      zipLayer.bindPopup('Zip boundary');
      zipLayer.addTo(map);
    }}
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    sample_zip = (sys.argv[1].strip() if len(sys.argv) > 1 else None) or None
    run_nces_plottable_test(sample_zip=sample_zip)

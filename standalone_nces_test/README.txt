NCES-only map test (no TIGER, no main app)
==========================================

This folder is for testing whether NCES school district boundaries load and draw
correctly, without touching the main app or TIGER zip boundaries.

Steps:
------
1. From the PROJECT ROOT (Data Site Selection Process), run:

   python standalone_nces_test/fetch_nces_districts.py 28202

   (Use any NC zip that has a boundary in data/zip_boundaries/.)

2. This will create:
   - nces_districts_28202.geojson  (raw NCES district polygons)
   - nces_only_map.html           (map that shows ONLY NCES districts)

3. Open nces_only_map.html in your browser:
   - Double-click the file, or
   - From project root: python -m http.server 8888
     Then go to: http://localhost:8888/standalone_nces_test/nces_only_map.html

What you should see:
--------------------
- A Leaflet/OpenStreetMap map with colored polygons = NCES district boundaries only.
- No TIGER outline, no zip boundary. If you see polygons, NCES is loading correctly.

If the map is empty:
--------------------
- Check the console when you ran fetch_nces_districts.py for "[FAIL]" messages.
- Open nces_districts_28202.geojson in https://geojson.io to confirm the geometry.

This test does not use the main app (app.py), frontend (map.js), or any TIGER
boundary drawing.

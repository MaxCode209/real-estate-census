"""Check if required dependencies for zone import are installed."""
import sys

print("Checking dependencies for NCES zone import...")
print("=" * 60)

# Check shapely
try:
    import shapely
    print("[OK] shapely: INSTALLED")
except ImportError:
    print("[MISSING] shapely: MISSING - run: pip install shapely")

# Check geopandas
try:
    import geopandas
    print("[OK] geopandas: INSTALLED")
except ImportError:
    print("[MISSING] geopandas: MISSING - run: pip install geopandas")

# Check fiona
try:
    import fiona
    print("[OK] fiona: INSTALLED")
except ImportError:
    print("[MISSING] fiona: MISSING - run: pip install fiona")
    print("   (If that fails, try: python -m pip install fiona)")

print("=" * 60)

# Check for NCES data
from pathlib import Path
nces_dir = Path("data/nces_zones")
shapefiles = list(nces_dir.glob("*.shp")) if nces_dir.exists() else []

if shapefiles:
    print(f"[OK] NCES data: FOUND ({len(shapefiles)} shapefile(s))")
    for shp in shapefiles:
        print(f"   - {shp.name}")
else:
    print("[MISSING] NCES data: NOT FOUND")
    print("   Download from: https://nces.ed.gov/programs/edge/sabs")
    print("   Place shapefiles in: data/nces_zones/")

print("=" * 60)

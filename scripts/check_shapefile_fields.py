"""Check what fields are actually in the SABS shapefile."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import geopandas as gpd

shapefile_path = Path('data/nces_zones/SABS_1516/SABS_1516.shp')

if not shapefile_path.exists():
    print(f"Shapefile not found: {shapefile_path}")
    sys.exit(1)

print("Reading shapefile to check available fields...")
gdf = gpd.read_file(str(shapefile_path))

print(f"\nTotal records: {len(gdf)}")
print(f"\nAll columns in shapefile:")
for i, col in enumerate(gdf.columns, 1):
    print(f"  {i}. {col}")

print(f"\nFirst few rows sample data:")
print(gdf.head(3).to_string())

# Check for school name fields
name_fields = [col for col in gdf.columns if 'NAME' in col.upper() or 'SCHOOL' in col.upper()]
print(f"\nFields containing 'NAME' or 'SCHOOL':")
for field in name_fields:
    print(f"  - {field}")
    sample_values = gdf[field].dropna().head(3).tolist()
    print(f"    Sample values: {sample_values}")

# Check for level fields
level_fields = [col for col in gdf.columns if 'LEVEL' in col.upper()]
print(f"\nFields containing 'LEVEL':")
for field in level_fields:
    print(f"  - {field}")
    unique_values = gdf[field].dropna().unique()[:10]
    print(f"    Unique values: {unique_values}")

# Check for state fields
state_fields = [col for col in gdf.columns if 'STATE' in col.upper()]
print(f"\nFields containing 'STATE':")
for field in state_fields:
    print(f"  - {field}")
    unique_values = gdf[field].dropna().unique()[:10]
    print(f"    Unique values: {unique_values}")

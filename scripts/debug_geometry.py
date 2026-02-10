"""Debug geometry conversion issue."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping

shapefile_path = 'data/nces_zones/SABS_1516/SABS_1516.shp'

print("Reading shapefile...")
gdf = gpd.read_file(shapefile_path)
print(f"Total zones: {len(gdf)}")

# Filter for NC and SC
gdf = gdf[gdf['stAbbrev'].isin(['NC', 'SC'])]
print(f"NC/SC zones: {len(gdf)}")

# Check first few rows
print("\nChecking first 5 zones:")
for i, (idx, row) in enumerate(gdf.head(5).iterrows()):
    print(f"\nZone {i+1} (index {idx}):")
    print(f"  School name: {row.get('schnam', 'N/A')}")
    print(f"  Geometry type: {type(row.geometry)}")
    print(f"  Is None: {row.geometry is None}")
    if hasattr(row.geometry, 'is_empty'):
        print(f"  Is empty: {row.geometry.is_empty}")
    if hasattr(row.geometry, 'geom_type'):
        print(f"  Geometry type: {row.geometry.geom_type}")
    
    # Try conversion
    try:
        geom_dict = mapping(row.geometry)
        print(f"  Conversion: SUCCESS - type: {geom_dict.get('type')}")
    except Exception as e:
        print(f"  Conversion: FAILED - {e}")

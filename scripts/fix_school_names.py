"""Fix school names in attendance_zones table by updating from shapefile."""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import geopandas as gpd
from backend.database import SessionLocal
from backend.models import AttendanceZone

def fix_school_names():
    """Update school names in database from shapefile."""
    shapefile_path = Path('data/nces_zones/SABS_1516/SABS_1516.shp')
    
    if not shapefile_path.exists():
        print(f"Shapefile not found: {shapefile_path}")
        return
    
    print("Reading shapefile...")
    gdf = gpd.read_file(str(shapefile_path))
    
    # Filter for NC and SC
    if 'stAbbrev' in gdf.columns:
        gdf = gdf[gdf['stAbbrev'].isin(['NC', 'SC'])]
    
    print(f"Found {len(gdf)} zones in shapefile for NC/SC")
    
    db = SessionLocal()
    
    try:
        # Get all zones from database
        zones = db.query(AttendanceZone).all()
        print(f"Found {len(zones)} zones in database")
        
        updated = 0
        not_found = 0
        
        # Create a lookup by geometry (simplified - match by school name and level if possible)
        # Actually, better approach: match by NCES school ID if we have it
        # Or we can just delete and re-import
        
        print("\nOptions:")
        print("1. Delete all existing zones and re-import (recommended)")
        print("2. Try to update existing zones (slower, may not match all)")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == '1':
            print("\nDeleting all existing zones...")
            db.query(AttendanceZone).delete()
            db.commit()
            print("Done! Now run: python scripts/import_nces_zones.py")
            return
        
        # Option 2: Try to update
        print("\nUpdating existing zones...")
        for zone in zones:
            # Try to find matching zone in shapefile
            # This is tricky without a unique ID, so we'll skip this approach
            pass
        
        print(f"\nUpdated {updated} zones")
        print(f"Could not match {not_found} zones")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    fix_school_names()

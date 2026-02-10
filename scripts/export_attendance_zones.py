"""Export attendance zones dataset to CSV/JSON for refining school zoning."""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import AttendanceZone
from config.config import Config

def export_attendance_zones_csv(output_file=None):
    """Export attendance zones to CSV (without GeoJSON - too large for CSV)."""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'data/attendance_zones_export_{timestamp}.csv'
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    db: Session = next(get_db())
    
    # Get all attendance zones
    zones = db.query(AttendanceZone).all()
    
    print(f"Found {len(zones)} attendance zones")
    
    if not zones:
        print("No attendance zones found in database.")
        return None
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Headers
        writer.writerow([
            'id',
            'school_id',
            'school_name',
            'school_level',
            'school_district',
            'state',
            'data_year',
            'source',
            'zone_boundary_size_chars',
            'created_at',
            'updated_at'
        ])
        
        # Data rows
        for zone in zones:
            boundary_size = len(zone.zone_boundary) if zone.zone_boundary else 0
            writer.writerow([
                zone.id,
                zone.school_id,
                zone.school_name,
                zone.school_level,
                zone.school_district,
                zone.state,
                zone.data_year,
                zone.source,
                boundary_size,
                zone.created_at.isoformat() if zone.created_at else None,
                zone.updated_at.isoformat() if zone.updated_at else None
            ])
    
    print(f"✅ Exported {len(zones)} zones to: {output_path}")
    return str(output_path)

def export_attendance_zones_json(output_file=None, include_geojson=True):
    """Export attendance zones to JSON (can include full GeoJSON)."""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'data/attendance_zones_export_{timestamp}.json'
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    db: Session = next(get_db())
    
    # Get all attendance zones
    zones = db.query(AttendanceZone).all()
    
    print(f"Found {len(zones)} attendance zones")
    
    if not zones:
        print("No attendance zones found in database.")
        return None
    
    # Convert to list of dicts
    zones_data = []
    for zone in zones:
        zone_dict = zone.to_dict()
        
        # Optionally exclude GeoJSON if too large
        if not include_geojson:
            zone_dict['zone_boundary'] = f"[GeoJSON - {len(zone.zone_boundary) if zone.zone_boundary else 0} chars]"
        
        zones_data.append(zone_dict)
    
    # Write JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'export_date': datetime.now().isoformat(),
            'total_zones': len(zones_data),
            'zones': zones_data
        }, f, indent=2, ensure_ascii=False)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ Exported {len(zones)} zones to: {output_path}")
    print(f"   File size: {file_size_mb:.2f} MB")
    return str(output_path)

def export_summary_stats():
    """Print summary statistics about attendance zones."""
    db: Session = next(get_db())
    
    zones = db.query(AttendanceZone).all()
    
    if not zones:
        print("No attendance zones found in database.")
        return
    
    print("\n" + "="*60)
    print("ATTENDANCE ZONES SUMMARY")
    print("="*60)
    print(f"Total zones: {len(zones)}")
    
    # By state
    states = {}
    for zone in zones:
        state = zone.state or 'Unknown'
        states[state] = states.get(state, 0) + 1
    
    print(f"\nBy State:")
    for state, count in sorted(states.items()):
        print(f"  {state}: {count}")
    
    # By school level
    levels = {}
    for zone in zones:
        level = zone.school_level or 'Unknown'
        levels[level] = levels.get(level, 0) + 1
    
    print(f"\nBy School Level:")
    for level, count in sorted(levels.items()):
        print(f"  {level}: {count}")
    
    # By district
    districts = {}
    for zone in zones:
        district = zone.school_district or 'Unknown'
        districts[district] = districts.get(district, 0) + 1
    
    print(f"\nTop 10 Districts:")
    sorted_districts = sorted(districts.items(), key=lambda x: x[1], reverse=True)[:10]
    for district, count in sorted_districts:
        print(f"  {district}: {count}")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    print("Exporting Attendance Zones Dataset...")
    print(f"Database: {Config.DATABASE_URL[:50]}...")
    
    # Show summary first
    export_summary_stats()
    
    # Export CSV (without GeoJSON - more manageable)
    csv_file = export_attendance_zones_csv()
    
    # Export JSON (with GeoJSON for full data)
    print("\nExporting JSON with full GeoJSON boundaries...")
    json_file = export_attendance_zones_json(include_geojson=True)
    
    print("\n" + "="*60)
    print("EXPORT COMPLETE")
    print("="*60)
    print(f"CSV file (summary): {csv_file}")
    print(f"JSON file (full data): {json_file}")
    print("\nYou can use these files to:")
    print("  1. Review zone coverage")
    print("  2. Identify missing zones")
    print("  3. Validate zone boundaries")
    print("  4. Refine school zoning logic")
    print("="*60)

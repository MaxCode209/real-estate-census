"""
Database migration script to add new columns to census_data table.
Adds: total_households, owner_occupied_units, renter_occupied_units,
      moved_from_different_state, moved_from_different_county, moved_from_abroad, net_migration_yoy
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.database import engine

def migrate_schema():
    """Add new columns to census_data table."""
    print("="*80)
    print("CENSUS DATA SCHEMA MIGRATION")
    print("="*80)
    print("\nAdding new columns to census_data table...")
    
    migrations = [
        ("total_households", "INTEGER"),
        ("owner_occupied_units", "INTEGER"),
        ("renter_occupied_units", "INTEGER"),
        ("moved_from_different_state", "INTEGER"),
        ("moved_from_different_county", "INTEGER"),
        ("moved_from_abroad", "INTEGER"),
        ("net_migration_yoy", "FLOAT"),
    ]
    
    with engine.connect() as conn:
        for column_name, column_type in migrations:
            try:
                # Check if column already exists
                check_sql = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='census_data' AND column_name='{column_name}'
                """)
                result = conn.execute(check_sql)
                if result.fetchone():
                    print(f"  [*] Column '{column_name}' already exists, skipping...")
                    continue
                
                # Add column
                alter_sql = text(f"ALTER TABLE census_data ADD COLUMN {column_name} {column_type}")
                conn.execute(alter_sql)
                conn.commit()
                print(f"  [+] Added column '{column_name}' ({column_type})")
            except Exception as e:
                print(f"  [-] Error adding column '{column_name}': {e}")
                conn.rollback()
    
    print("\n" + "="*80)
    print("Migration complete!")
    print("="*80)
    print("\nNext steps:")
    print("1. Update existing records with new data:")
    print("   python scripts/add_state_county_to_census.py")
    print("2. Fetch 2023 data for all zip codes:")
    print("   python scripts/fetch_census_data.py")

if __name__ == '__main__':
    migrate_schema()

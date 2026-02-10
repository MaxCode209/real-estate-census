"""
Script to calculate net migration YoY for existing census_data records.
Calculates: (population_2023 - population_2022) / population_2022 * 100
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import CensusData

def calculate_net_migration():
    """Calculate net migration YoY for all zip codes that have both 2022 and 2023 data."""
    db = SessionLocal()
    
    try:
        print("="*80)
        print("CALCULATING NET MIGRATION YoY")
        print("="*80)
        print("\nFormula: (population_2023 - population_2022) / population_2022 * 100\n")
        
        # Get all zip codes
        all_zips = db.query(CensusData.zip_code).distinct().all()
        zip_codes = [z[0] for z in all_zips]
        
        print(f"Found {len(zip_codes)} unique zip codes")
        
        calculated = 0
        skipped_no_2022 = 0
        skipped_no_2023 = 0
        
        for zip_code in zip_codes:
            # Get 2022 and 2023 records
            data_2022 = db.query(CensusData).filter(
                CensusData.zip_code == zip_code,
                CensusData.data_year == '2022'
            ).first()
            
            data_2023 = db.query(CensusData).filter(
                CensusData.zip_code == zip_code,
                CensusData.data_year == '2023'
            ).first()
            
            if not data_2022:
                skipped_no_2022 += 1
                continue
            
            if not data_2023:
                skipped_no_2023 += 1
                continue
            
            pop_2022 = data_2022.population
            pop_2023 = data_2023.population
            
            if not pop_2022 or not pop_2023 or pop_2022 == 0:
                continue
            
            # Calculate net migration YoY
            net_migration_yoy = ((pop_2023 - pop_2022) / pop_2022) * 100
            
            # Update 2023 record with calculated value
            data_2023.net_migration_yoy = net_migration_yoy
            calculated += 1
            
            if calculated % 100 == 0:
                db.commit()
                print(f"  Calculated for {calculated} zip codes...")
        
        db.commit()
        
        print("\n" + "="*80)
        print("CALCULATION COMPLETE")
        print("="*80)
        print(f"  Calculated net migration: {calculated} zip codes")
        print(f"  Skipped (no 2022 data): {skipped_no_2022} zip codes")
        print(f"  Skipped (no 2023 data): {skipped_no_2023} zip codes")
        print("="*80)
        
    finally:
        db.close()

if __name__ == '__main__':
    calculate_net_migration()

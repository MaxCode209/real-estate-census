"""
Bulk import ALL census data for all US zip codes.
This is a one-time operation to populate the entire census_data table.
Once complete, you won't need to call the Census API on-demand.
"""
import sys
import os
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.census_api import CensusAPIClient
from backend.models import CensusData

def bulk_import_all_census_data():
    """Fetch and store ALL census data for all US zip codes."""
    print("=" * 80)
    print("BULK IMPORT: ALL CENSUS DATA")
    print("=" * 80)
    print("\nThis will fetch census data for ALL US zip codes from the Census API.")
    print("This is a one-time operation that may take 5-15 minutes.")
    print("Once complete, you'll have all census data in your database.\n")
    
    db = SessionLocal()
    client = CensusAPIClient()
    
    try:
        # Check current count
        current_count = db.query(CensusData).count()
        print(f"[INFO] Current census records in database: {current_count}")
        
        print("\n[STEP 1] Fetching ALL census data from Census Bureau API...")
        print("  This may take several minutes (fetching ~33,000 zip codes)...")
        print("  Progress will be shown below:\n")
        
        start_time = time.time()
        
        # Fetch ALL zip codes (pass None to get all)
        census_data = client.fetch_zip_code_data(zip_codes=None)
        
        fetch_time = time.time() - start_time
        print(f"\n[STEP 1 COMPLETE] Fetched {len(census_data)} records in {fetch_time:.1f} seconds")
        
        if not census_data:
            print("[ERROR] No data returned from Census API")
            print("  - Check your internet connection")
            print("  - Verify Census API is accessible")
            print("  - Check config/config.py for correct API settings")
            return
        
        print(f"\n[STEP 2] Storing records in database...")
        print("  This will update existing records and add new ones...\n")
        
        added = 0
        updated = 0
        skipped = 0
        errors = 0
        
        total = len(census_data)
        start_time = time.time()
        
        # Process in batches for better progress tracking
        batch_size = 100
        for i in range(0, total, batch_size):
            batch = census_data[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            for data in batch:
                try:
                    zip_code = data.get('zip_code')
                    if not zip_code:
                        skipped += 1
                        continue
                    
                    existing = db.query(CensusData).filter(
                        CensusData.zip_code == zip_code
                    ).first()
                    
                    if existing:
                        # Update existing record
                        for key, value in data.items():
                            if hasattr(existing, key) and key != 'id':
                                setattr(existing, key, value)
                        updated += 1
                    else:
                        # Create new record
                        new_record = CensusData(**data)
                        db.add(new_record)
                        added += 1
                    
                except Exception as e:
                    errors += 1
                    if errors <= 5:  # Only show first 5 errors
                        print(f"  [ERROR] Failed to process zip {data.get('zip_code', 'unknown')}: {e}")
                    continue
            
            # Commit batch
            try:
                db.commit()
            except Exception as e:
                print(f"  [ERROR] Failed to commit batch {batch_num}: {e}")
                db.rollback()
                continue
            
            # Progress update
            processed = min(i + batch_size, total)
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            remaining = (total - processed) / rate if rate > 0 else 0
            
            print(f"  Batch {batch_num}/{total_batches}: {processed}/{total} records "
                  f"({added} added, {updated} updated, {skipped} skipped, {errors} errors)")
            if remaining > 0:
                print(f"    Estimated time remaining: {remaining/60:.1f} minutes")
        
        total_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print("BULK IMPORT COMPLETE")
        print(f"{'='*80}")
        print(f"  Total records fetched: {len(census_data)}")
        print(f"  Added: {added} new records")
        print(f"  Updated: {updated} existing records")
        print(f"  Skipped: {skipped} records (missing zip_code)")
        print(f"  Errors: {errors} records")
        print(f"  Total time: {total_time/60:.1f} minutes")
        
        # Final count
        final_count = db.query(CensusData).count()
        print(f"\n  Final census records in database: {final_count}")
        print(f"{'='*80}\n")
        
        print("[SUCCESS] All census data has been imported!")
        print("  You can now search for any zip code without calling the API.")
        print("  The system will use the database instead of making API calls.\n")
        
    except Exception as e:
        print(f"\n[ERROR] Bulk import failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    # Confirm before proceeding
    print("\n" + "=" * 80)
    print("WARNING: This will fetch ALL US census data (~33,000 zip codes)")
    print("=" * 80)
    print("\nThis operation:")
    print("  - Will take 5-15 minutes to complete")
    print("  - Will make one large API call to Census Bureau")
    print("  - Will populate your entire census_data table")
    print("  - Will update existing records and add new ones")
    print("\nPress Ctrl+C to cancel, or")
    
    try:
        response = input("Press Enter to continue... ")
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    
    print("\n")
    bulk_import_all_census_data()

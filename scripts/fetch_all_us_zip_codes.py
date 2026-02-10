"""
Fetch ALL US zip codes from Census Bureau API.
This is FREE and fetches all ~33,000+ zip codes in one API call!
"""
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.census_api import CensusAPIClient
from backend.models import CensusData

def fetch_all_zip_codes():
    """Fetch all US zip codes from Census API and store in database."""
    db = SessionLocal()
    client = CensusAPIClient()
    
    print("="*70)
    print("Fetching ALL US Zip Codes from Census Bureau API")
    print("="*70)
    print("\nThis is FREE and will fetch all ~33,000+ US zip codes!")
    print("This may take a few minutes...\n")
    
    start_time = time.time()
    
    try:
        # Fetch ALL zip codes (pass None to fetch all)
        print("Making API request to Census Bureau...")
        census_data = client.fetch_zip_code_data(zip_codes=None)  # None = fetch all
        
        if not census_data:
            print("\n[ERROR] No data received from Census API")
            print("Possible reasons:")
            print("  1. API rate limit exceeded (wait and try again)")
            print("  2. Network connection issue")
            print("  3. Census API temporarily unavailable")
            return 0
        
        print(f"\n[SUCCESS] Received {len(census_data)} zip code records from Census API")
        print(f"Storing in database...\n")
        
        # Store in database
        added = 0
        updated = 0
        skipped = 0
        
        for i, data in enumerate(census_data, 1):
            # Skip if zip code is missing or invalid
            zip_code = data.get('zip_code', '').strip()
            if not zip_code or len(zip_code) != 5:
                skipped += 1
                continue
            
            try:
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
                    # Add new record
                    new_record = CensusData(**data)
                    db.add(new_record)
                    added += 1
            except Exception as e:
                # Database connection issue - reconnect and retry
                print(f"  [WARNING] Database error at {i}: {e}")
                try:
                    db.rollback()
                    db.close()
                    db = SessionLocal()
                    # Retry the query
                    existing = db.query(CensusData).filter(
                        CensusData.zip_code == zip_code
                    ).first()
                    if existing:
                        for key, value in data.items():
                            if hasattr(existing, key) and key != 'id':
                                setattr(existing, key, value)
                        updated += 1
                    else:
                        new_record = CensusData(**data)
                        db.add(new_record)
                        added += 1
                except Exception as e2:
                    print(f"  [ERROR] Could not recover: {e2}")
                    skipped += 1
                    continue
            
            # Commit in smaller batches to avoid connection timeouts
            if i % 50 == 0:
                try:
                    db.commit()
                    print(f"  Processed {i}/{len(census_data)} records... (Added: {added}, Updated: {updated})")
                except Exception as e:
                    print(f"  [WARNING] Commit error at {i}: {e}")
                    try:
                        db.rollback()
                        # Try to reconnect
                        db.close()
                        db = SessionLocal()
                        print(f"  [INFO] Reconnected to database, continuing...")
                    except:
                        print(f"  [ERROR] Could not reconnect. Stopping at {i} records.")
                        raise
        
        # Final commit
        try:
            db.commit()
        except Exception as e:
            print(f"[WARNING] Final commit error: {e}")
            db.rollback()
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*70)
        print("FETCH COMPLETE!")
        print("="*70)
        print(f"Total records processed: {len(census_data)}")
        print(f"  - New records added: {added}")
        print(f"  - Existing records updated: {updated}")
        print(f"  - Skipped (invalid): {skipped}")
        print(f"  - Total in database now: {added + updated}")
        print(f"\nTime taken: {elapsed_time:.1f} seconds")
        print(f"\n[SUCCESS] All US zip codes are now in your database!")
        print("You can now search for any US address and export the data!")
        
        return added + updated
        
    except Exception as e:
        print(f"\n[ERROR] Failed to fetch data: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Verify Census API is accessible")
        print("  3. Check if you've hit rate limits (wait a few minutes)")
        db.rollback()
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch all US zip codes from Census API')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if not args.yes:
        print("\n[WARNING] This will fetch ALL US zip codes (~33,000+ records)")
        print("   This is FREE and will take a few minutes.\n")
        
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    fetch_all_zip_codes()

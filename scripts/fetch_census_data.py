"""Script to fetch census data from Census Bureau API and store in database."""
import sys
import os
import time
from datetime import datetime, timezone, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from backend.database import SessionLocal, engine
from backend.census_api import CensusAPIClient
from backend.models import CensusData

BATCH_SIZE = 50   # Census API batch; we commit in smaller chunks to avoid Supabase statement timeout
COMMIT_CHUNK_SIZE = 10   # Commit at most this many rows per transaction (avoids statement timeout)
COMMIT_RETRIES = 3   # Retry commit this many times on connection drop or statement timeout
COMMIT_RETRY_DELAY = 10   # Seconds to wait before retry


def _ensure_census_schema_migrated():
    """Run migration if needed: rename average_household_income -> median_household_income, drop state/county."""
    with engine.connect() as conn:
        # Supabase often has a short statement timeout; ALTER on large tables can exceed it.
        # Raise timeout to 10 minutes for this connection (migration only).
        try:
            conn.execute(text("SET statement_timeout = '600000'"))  # 10 min in ms
            conn.commit()
        except Exception:
            conn.rollback()

        # Rename column if old name still exists
        try:
            r = conn.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'census_data' AND column_name = 'average_household_income'
            """))
            if r.fetchone() is not None:
                conn.execute(text("ALTER TABLE census_data RENAME COLUMN average_household_income TO median_household_income"))
                conn.commit()
                print("  [Migration] Renamed average_household_income -> median_household_income")
        except Exception as e:
            conn.rollback()
            err = str(e).lower()
            if "timeout" in err or "querycanceled" in err or "canceled" in err:
                print("  [Migration] ALTER timed out (Supabase limits long DDL). Run the migration in Supabase SQL Editor:")
                print("    1. Supabase Dashboard → SQL Editor")
                print("    2. Run: ALTER TABLE census_data RENAME COLUMN average_household_income TO median_household_income;")
                print("    3. Run: ALTER TABLE census_data DROP COLUMN IF EXISTS state; ALTER TABLE census_data DROP COLUMN IF EXISTS county;")
                print("  Then run this script again: python scripts/fetch_census_data.py --from-db --refresh")
                sys.exit(1)
            if "does not exist" not in err:
                raise
        # Drop state/county if present
        for col in ('state', 'county'):
            try:
                r = conn.execute(text("""
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'census_data' AND column_name = :col
                """), {"col": col})
                if r.fetchone() is not None:
                    conn.execute(text(f"ALTER TABLE census_data DROP COLUMN {col}"))
                    conn.commit()
                    print(f"  [Migration] Dropped column {col}")
            except Exception:
                conn.rollback()


def _store_batch(db, batch_data):
    """Compute net_migration_yoy (2024 vs 2023) and upsert one batch; caller must commit."""
    added, updated = 0, 0
    for data in batch_data:
        zip_code = data['zip_code']
        pop_current = data.get('population', 0)  # 2024 from API
        existing = db.query(CensusData).filter(CensusData.zip_code == zip_code).first()
        # Prior year = 2023 (for YoY: (2024 - 2023) / 2023 * 100)
        data_prior = db.query(CensusData).filter(
            CensusData.zip_code == zip_code,
            CensusData.data_year == '2023'
        ).first()
        if data_prior and data_prior.population and pop_current and data_prior.population > 0:
            data['net_migration_yoy'] = ((pop_current - data_prior.population) / data_prior.population) * 100
        else:
            data['net_migration_yoy'] = None
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.now(timezone.utc)
            updated += 1
        else:
            db.add(CensusData(**data))
            added += 1
    return added, updated


def _is_retryable_db_error(e):
    """True if we should retry after rollback (connection drop or statement timeout)."""
    msg = str(e).lower()
    return (
        "closed the connection" in msg
        or "connection" in msg
        or "statement timeout" in msg
        or "querycanceled" in msg
        or "canceling statement" in msg
    )


def _commit_with_retry(db):
    """Commit and retry on connection drop or statement timeout (e.g. Supabase)."""
    for attempt in range(COMMIT_RETRIES):
        try:
            db.commit()
            return True
        except OperationalError as e:
            db.rollback()
            if _is_retryable_db_error(e) and attempt < COMMIT_RETRIES - 1:
                print(f"  DB timeout/connection issue; waiting {COMMIT_RETRY_DELAY}s then retrying ({attempt + 1}/{COMMIT_RETRIES})...")
                time.sleep(COMMIT_RETRY_DELAY)
                continue
            raise
    return False


def fetch_and_store(zip_codes=None, limit=None):
    """Fetch census data and store in database. Commits in small chunks to avoid Supabase statement timeout."""
    client = CensusAPIClient()

    if zip_codes:
        if limit:
            zip_codes = zip_codes[:limit]
        n = len(zip_codes)
        total_batches = (n + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Fetching 2024 census data for {n} zip codes (API batch {BATCH_SIZE}, commit chunk {COMMIT_CHUNK_SIZE}).")
        print("Writing to DB in small chunks to avoid statement timeout; updated_at set on every update.\n")
        total_added, total_updated = 0, 0
        for i in range(0, n, BATCH_SIZE):
            batch = zip_codes[i:i + BATCH_SIZE]
            batch_data = client.fetch_zip_code_data(batch)
            batch_added, batch_updated = 0, 0
            # Commit in small chunks so each transaction stays under Supabase statement timeout
            for chunk_start in range(0, len(batch_data), COMMIT_CHUNK_SIZE):
                chunk = batch_data[chunk_start:chunk_start + COMMIT_CHUNK_SIZE]
                for attempt in range(COMMIT_RETRIES):
                    db = SessionLocal()
                    try:
                        added, updated = _store_batch(db, chunk)
                        db.commit()
                        batch_added += added
                        batch_updated += updated
                        break
                    except OperationalError as e:
                        db.rollback()
                        if _is_retryable_db_error(e) and attempt < COMMIT_RETRIES - 1:
                            print(f"  Statement timeout/connection issue; waiting {COMMIT_RETRY_DELAY}s then retrying chunk ({attempt + 1}/{COMMIT_RETRIES})...")
                            time.sleep(COMMIT_RETRY_DELAY)
                            continue
                        raise
                    finally:
                        db.close()
            total_added += batch_added
            total_updated += batch_updated
            done = min(i + BATCH_SIZE, n)
            pct = (100 * done) // n
            batch_num = i // BATCH_SIZE + 1
            print(f"  Batch {batch_num}/{total_batches}: {done}/{n} zips ({pct}%) — added {batch_added}, updated {batch_updated}")
        print(f"\nDone. Stored {total_added} new records and updated {total_updated} existing records.")
        return total_added + total_updated
    else:
        print("Fetching census data from Census Bureau API (all ZCTAs)...")
        census_data = client.fetch_zip_code_data(None)
        if limit:
            census_data = census_data[:limit]
        print(f"Fetched {len(census_data)} records total")
        db = SessionLocal()
        try:
            added, updated = _store_batch(db, census_data)
            _commit_with_retry(db)
            print(f"\nStored {added} new records and updated {updated} existing records")
            return added + updated
        finally:
            db.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch census data from Census Bureau API')
    parser.add_argument('--zip-codes', nargs='+', help='Specific zip codes to fetch')
    parser.add_argument('--limit', type=int, help='Limit number of records to fetch')
    parser.add_argument('--from-db', action='store_true', help='Use all zip codes from census_data table')
    parser.add_argument('--refresh', action='store_true', help='Re-fetch and overwrite 2024 rows (Median HHI in average_household_income, 0s for counts). Use with --from-db to refresh all zips.')
    parser.add_argument('--resume-refresh', action='store_true', help='With --from-db --refresh: skip zips updated in the last 2 hours (resume after a failed run).')
    
    args = parser.parse_args()
    
    zip_codes = args.zip_codes
    if args.from_db:
        db = SessionLocal()
        try:
            from sqlalchemy import and_
            all_zips = [r[0] for r in db.query(CensusData.zip_code).distinct().all()]
            if args.refresh:
                zip_codes = all_zips
                if args.resume_refresh:
                    cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
                    skip = {r[0] for r in db.query(CensusData.zip_code).filter(
                        CensusData.data_year == '2024',
                        CensusData.updated_at >= cutoff
                    ).distinct().all()}
                    zip_codes = [z for z in all_zips if z not in skip]
                    print(f"Resume refresh: skipping {len(skip)} zips updated in last 2h; {len(zip_codes)} zips to process.")
                print(f"Using {len(zip_codes)} zip codes to re-fetch and overwrite 2024 data (Median HHI in average_household_income, complete columns).")
                # No DDL: table keeps average_household_income, state, county to avoid Supabase timeouts.
                print("")
            else:
                done = {r[0] for r in db.query(CensusData.zip_code).filter(
                    and_(CensusData.data_year == '2024', CensusData.population.isnot(None))
                ).all()}
                zip_codes = [z for z in all_zips if z not in done]
                print(f"Using {len(zip_codes)} zip codes to fetch (skipping {len(done)} already with 2024 data)")
            if not zip_codes:
                print("Nothing to do — no zip codes to fetch.")
                db.close()
                sys.exit(0)
        finally:
            db.close()
    
    fetch_and_store(
        zip_codes=zip_codes,
        limit=args.limit
    )


"""
Add 'city' column to census_data table.
Run once: python scripts/migrate_add_city_to_census.py

Uses DIRECT connection (port 5432) and a long statement timeout to avoid
Supabase pooler timeouts. If your .env uses the pooler, the script switches
to the direct host for this project.

Set DATABASE_URL in .env to either:
  - Pooler:  postgresql://postgres.[ref]:[PASSWORD]@aws-0-xxx.pooler.supabase.com:6543/postgres
  - Direct:  postgresql://postgres:[PASSWORD]@db.naixizrmldynltbaioem.supabase.co:5432/postgres
(Replace [PASSWORD] with your database password from Supabase Dashboard → Settings → Database.)

Then assign cities via: python scripts/assign_city_from_csv.py or fetch_city_for_zips.py
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from config.config import Config

# Direct connection for this Supabase project (avoids pooler statement timeout)
_SUPABASE_DIRECT_HOST = "db.naixizrmldynltbaioem.supabase.co"
_SUPABASE_DIRECT_PORT = "5432"

_db_url_original = Config.DATABASE_URL
_db_url = _db_url_original
# If using pooler (pooler.supabase.com or port 6543), switch to direct host:port
if "pooler" in _db_url or ":6543" in _db_url:
    _db_url = re.sub(
        r"@[^/@]+:(?:6543|5432)(?=/)",
        f"@{_SUPABASE_DIRECT_HOST}:{_SUPABASE_DIRECT_PORT}",
        _db_url,
        count=1,
    )
    if ":6543" in _db_url:
        _db_url = _db_url.replace(":6543", ":5432", 1)
    print("  [*] Using direct connection to avoid pooler timeout.")

ENGINE = create_engine(
    _db_url,
    connect_args={"connect_timeout": 30},
    pool_pre_ping=True,
)
# Fallback URL (pooler) if direct host is unreachable (e.g. DNS)
ENGINE_FALLBACK = create_engine(
    _db_url_original,
    connect_args={"connect_timeout": 30},
    pool_pre_ping=True,
)
# 5 minutes (Supabase can kill long-running statements; direct connection usually allows this)
STATEMENT_TIMEOUT_MS = 300000


def migrate():
    print("=" * 60)
    print("CENSUS DATA: Add 'city' column")
    print("=" * 60)
    print("Connecting to database...")
    sys.stdout.flush()

    engine = ENGINE
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        if "translate host" in str(e).lower() or "could not connect" in str(e).lower():
            print("  [*] Direct host unreachable, using pooler connection.")
            engine = ENGINE_FALLBACK
        else:
            raise

    with engine.connect() as conn:
        try:
            # Raise statement timeout so ALTER/INDEX don't hit pooler limit (e.g. 8s)
            conn.execute(text(f"SET statement_timeout = '{STATEMENT_TIMEOUT_MS}'"))
            conn.commit()

            check_sql = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'census_data' AND column_name = 'city'
            """)
            result = conn.execute(check_sql)
            if result.fetchone():
                print("  [*] Column 'city' already exists. Nothing to do.")
                return
            print("  Adding column 'city' (this can take a moment on large tables)...")
            sys.stdout.flush()
            alter_sql = text("ALTER TABLE census_data ADD COLUMN city VARCHAR(100) NULL")
            conn.execute(alter_sql)
            conn.commit()
            print("  [+] Added column 'city' (VARCHAR(100) NULL)")
        except Exception as e:
            conn.rollback()
            print(f"  [-] Error: {e}")
            raise

    # Create index for filtering by city (optional; helps GET /api/census-data?city=...)
    print("  Creating index on city (if not exists)...")
    sys.stdout.flush()
    with engine.connect() as conn:
        try:
            conn.execute(text(f"SET statement_timeout = '{STATEMENT_TIMEOUT_MS}'"))
            conn.commit()
            idx_sql = text("""
                CREATE INDEX IF NOT EXISTS idx_census_data_city ON census_data (city)
            """)
            conn.execute(idx_sql)
            conn.commit()
            print("  [+] Index idx_census_data_city created (or already exists)")
        except Exception as e:
            conn.rollback()
            print(f"  [*] Index creation skipped or already exists: {e}")

    print("=" * 60)
    print("Next: assign cities to zip codes.")
    print("  1. Export zips:  python scripts/export_zips_for_city.py")
    print("  2. Add a 'city' column in the CSV and fill in city names.")
    print("  3. Run:          python scripts/assign_city_from_csv.py")
    print("=" * 60)


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        err = str(e).lower()
        if "timeout" in err or "canceled" in err:
            print("\n--- Timeout fix: use DIRECT connection ---")
            print("  1. Supabase Dashboard → Project Settings → Database")
            print("  2. Under 'Connection string', open the dropdown and select 'URI'.")
            print("  3. Copy the DIRECT connection (host like db.xxxx.supabase.co, port 5432).")
            print("  4. In .env set DATABASE_URL to that full URI, then run this script again.")
        raise

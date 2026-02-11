"""
Import NC Top Employers dataset into the county_employers table.

Usage examples:
    python scripts/import_county_employers.py
    python scripts/import_county_employers.py --dry-run --limit 20
"""
from __future__ import annotations

import argparse
import csv
import itertools
import os
import pathlib
import re
import sys
from typing import Dict, Iterable, List, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func

from backend.database import SessionLocal
from backend.models import CountyEmployer

DEFAULT_CSV_PATH = pathlib.Path(
    r"c:\Users\Max\OneDrive - Edgehill Real Estate Capital\Desktop\Data Project Datasets\NC_Top_Employers_with_Salaries.csv"  # noqa: E501
)
BATCH_SIZE = 500
SALARY_CLEAN_RE = re.compile(r"[^\d]")
NC_COUNTY_FIPS = None
NC_COUNTY_CSV = pathlib.Path(PROJECT_ROOT, "data", "nc_county_fips.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import NC Top Employers dataset into Supabase.")
    parser.add_argument(
        "--csv-path",
        type=pathlib.Path,
        default=DEFAULT_CSV_PATH,
        help="Path to NC_Top_Employers_with_Salaries.csv (default: %(default)s)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Maximum rows to import (debugging).")
    parser.add_argument("--dry-run", action="store_true", help="Parse and log results without writing to the DB.")
    return parser.parse_args()


def clean_text(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None
    cleaned = val.strip()
    return cleaned if cleaned else None


def normalize_sector_class(raw: Optional[str]) -> Optional[str]:
    value = clean_text(raw)
    if not value:
        return None
    lowered = value.lower()
    if "private" in lowered:
        return "private_sector"
    if "public" in lowered:
        return "public_sector"
    return value.replace(" ", "_").lower()


def normalize_employment_range(raw: Optional[str]) -> Optional[str]:
    value = clean_text(raw)
    return value


def parse_salary(raw: Optional[str]) -> Optional[int]:
    value = clean_text(raw)
    if not value:
        return None
    digits = SALARY_CLEAN_RE.sub("", value)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def parse_int(raw: Optional[str]) -> Optional[int]:
    value = clean_text(raw)
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def normalize_county_key(name: Optional[str]) -> Optional[str]:
    value = clean_text(name)
    if not value:
        return None
    lowered = value.lower()
    lowered = lowered.replace(" county", "")
    lowered = lowered.replace(" city", "")
    lowered = lowered.replace(".", "")
    lowered = lowered.replace("-", " ")
    lowered = " ".join(lowered.split())
    return lowered


def build_nc_county_lookup() -> Dict[str, str]:
    if not NC_COUNTY_CSV.exists():
        raise SystemExit(f"Missing {NC_COUNTY_CSV}. Run the nc_county_fips download step first.")
    lookup: Dict[str, str] = {}
    with NC_COUNTY_CSV.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = normalize_county_key(row.get("county_name"))
            value = row.get("county_fips")
            if key and value:
                # Compose full 5-digit FIPS string using state + county codes
                state_fips = row.get("state_fips", "37").zfill(2)
                lookup[key] = f"{state_fips}{value.zfill(3)}"
    return lookup


def lookup_county_fips(county_name: Optional[str]) -> Optional[str]:
    global NC_COUNTY_FIPS
    if NC_COUNTY_FIPS is None:
        NC_COUNTY_FIPS = build_nc_county_lookup()
    key = normalize_county_key(county_name)
    if not key:
        return None
    return NC_COUNTY_FIPS.get(key)


def iter_csv_rows(path: pathlib.Path) -> Iterable[Dict[str, object]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            county_name = clean_text(raw.get("Area Name"))
            if not county_name:
                continue
            year = parse_int(raw.get("Year")) or 2024
            company_name = clean_text(raw.get("Company Name"))
            if not company_name:
                continue
            industry = clean_text(raw.get("Industry"))
            sector_class = normalize_sector_class(raw.get("Class")) or "private_sector"
            employment_range = normalize_employment_range(raw.get("Employment Range")) or "Unknown"
            rank = parse_int(raw.get("Rank")) or 0
            avg_salary = parse_salary(raw.get("Avg Salary"))
            county_fips = lookup_county_fips(county_name)

            yield {
                "county_name": county_name,
                "state_code": "NC",
                "county_fips": county_fips,
                "year": year,
                "company_name": company_name,
                "industry": industry,
                "sector_class": sector_class,
                "employment_range": employment_range,
                "rank": rank,
                "avg_salary": avg_salary,
            }


def chunked(iterable: Iterable[Dict[str, object]], size: int) -> Iterable[List[Dict[str, object]]]:
    iterator = iter(iterable)
    while True:
        batch = list(itertools.islice(iterator, size))
        if not batch:
            break
        yield batch


def upsert_rows(session, rows: List[Dict[str, object]], dry_run: bool) -> int:
    if dry_run or not rows:
        return len(rows)
    insert_stmt = insert(CountyEmployer).values(rows)
    stmt = insert_stmt.on_conflict_do_update(
        index_elements=["county_name", "year", "company_name", "rank"],
        set_={
            "industry": insert_stmt.excluded.industry,
            "sector_class": insert_stmt.excluded.sector_class,
            "employment_range": insert_stmt.excluded.employment_range,
            "avg_salary": insert_stmt.excluded.avg_salary,
            "county_fips": insert_stmt.excluded.county_fips,
            "updated_at": func.now(),
        },
    )
    session.execute(stmt)
    session.commit()
    return len(rows)


def main():
    args = parse_args()
    csv_path = args.csv_path.resolve()
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    rows_iter = iter_csv_rows(csv_path)
    if args.limit:
        rows_iter = itertools.islice(rows_iter, args.limit)

    parsed_rows = list(rows_iter)
    print(f"Parsed {len(parsed_rows)} rows from {csv_path}")

    session = SessionLocal()
    try:
        affected = 0
        for batch in chunked(parsed_rows, BATCH_SIZE):
            affected += upsert_rows(session, batch, args.dry_run)
        action = "would process" if args.dry_run else "processed"
        print(f"{action.capitalize()} {affected} rows (full upsert).")
    finally:
        session.close()


if __name__ == "__main__":
    main()

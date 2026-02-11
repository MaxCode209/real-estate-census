"""
Quick sanity checks for the county_employers table.

Usage:
    python scripts/check_employment_data.py
"""
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import func

from backend.database import SessionLocal
from backend.models import CountyEmployer


def main():
    session = SessionLocal()
    try:
        total_rows = session.query(func.count(CountyEmployer.id)).scalar() or 0
        counties_with_rows = session.query(func.count(func.distinct(CountyEmployer.county_name))).scalar() or 0
        rows_with_salary = session.query(func.count(CountyEmployer.id)).filter(CountyEmployer.avg_salary.isnot(None)).scalar() or 0
        rows_without_fips = (
            session.query(func.count(CountyEmployer.id))
            .filter(CountyEmployer.county_fips.is_(None))
            .scalar()
            or 0
        )

        print(f"county_employers rows: {total_rows:,}")
        print(f"counties with at least one employer: {counties_with_rows}")
        print(f"rows that include avg_salary: {rows_with_salary:,}")
        print(f"rows missing county_fips: {rows_without_fips:,}")

        top_counties = (
            session.query(CountyEmployer.county_name, func.count().label("employers"))
            .group_by(CountyEmployer.county_name)
            .order_by(func.count().desc())
            .limit(5)
            .all()
        )
        if top_counties:
            print("\nTop counties by employer count:")
            for county, count in top_counties:
                print(f"  {county:<25} {count:>4}")

        missing_salary = (
            session.query(CountyEmployer.county_name, func.count().label("missing_salary"))
            .filter(CountyEmployer.avg_salary.is_(None))
            .group_by(CountyEmployer.county_name)
            .order_by(func.count().desc())
            .limit(5)
            .all()
        )
        if missing_salary:
            print("\nCounties with the most missing avg_salary values:")
            for county, count in missing_salary:
                print(f"  {county:<25} {count:>4}")
    finally:
        session.close()


if __name__ == "__main__":
    main()

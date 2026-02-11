"""Quick script to check county population progress."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
r = db.execute(text("SELECT COUNT(*) FROM census_data WHERE county IS NOT NULL AND TRIM(county) != ''")).scalar()
t = db.execute(text("SELECT COUNT(*) FROM census_data")).scalar()
print(f"{r}/{t} zips have county")
db.close()

"""Quick test: does city filter work?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
params = {"city": "Charlotte"}
where_sql = "LOWER(TRIM(COALESCE(city, ''))) = LOWER(TRIM(:city))"
cnt = db.execute(text("SELECT COUNT(*) FROM census_data WHERE " + where_sql), params).scalar()
print("Charlotte zips:", cnt)
rows = db.execute(
    text("SELECT zip_code, city FROM census_data WHERE " + where_sql + " LIMIT 5"),
    params
).fetchall()
print("Sample:", rows)
db.close()

"""Clear bad school data cache entries."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import SchoolData

db = SessionLocal()

# Delete all entries with null ratings
bad_entries = db.query(SchoolData).filter(
    SchoolData.elementary_school_rating.is_(None),
    SchoolData.middle_school_rating.is_(None),
    SchoolData.high_school_rating.is_(None)
).all()

print(f"Found {len(bad_entries)} entries with null ratings")
for entry in bad_entries:
    print(f"  Deleting entry {entry.id}: {entry.address}")
    db.delete(entry)

db.commit()
print(f"Deleted {len(bad_entries)} bad cache entries")
db.close()

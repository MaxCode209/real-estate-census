"""
Optional script to create a zip code centroids table for faster geocoding.
This improves map performance by avoiding geocoding API calls.

You can populate this table with data from:
- https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html
- Or use a commercial zip code database
"""
from backend.database import Base, engine, SessionLocal
from sqlalchemy import Column, String, Float, Index

class ZipCodeCentroid(Base):
    """Model for storing zip code centroids (lat/lng)."""
    
    __tablename__ = 'zip_code_centroids'
    
    zip_code = Column(String(10), primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    state = Column(String(2), nullable=True)
    
    def to_dict(self):
        return {
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'state': self.state
        }

def create_table():
    """Create the zip code centroids table."""
    ZipCodeCentroid.__table__.create(bind=engine, checkfirst=True)
    print("Zip code centroids table created!")

if __name__ == '__main__':
    create_table()
    print("\nTo populate this table, you can:")
    print("1. Download zip code centroids from Census Bureau")
    print("2. Use a commercial zip code database")
    print("3. Manually import CSV data")


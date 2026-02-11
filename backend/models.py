"""Database models for census data."""
from sqlalchemy import Column, String, Float, Integer, DateTime, Index, Text, ForeignKey, Numeric, UniqueConstraint, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base

class CensusData(Base):
    """Model for storing census data by zip code."""
    
    __tablename__ = 'census_data'
    
    id = Column(Integer, primary_key=True, index=True)
    zip_code = Column(String(10), nullable=False, unique=True, index=True)  # Unique constraint prevents duplicates
    county = Column(String(100), nullable=True)  # kept for schema; not populated (avoids DDL timeout)

    # Census data fields (2024). average_household_income = Census B19013 (Median HHI); label in UI as "MHI"
    population = Column(Integer, nullable=True)
    median_age = Column(Float, nullable=True)
    average_household_income = Column(Float, nullable=True)  # Census B19013_001E (Median HHI)
    city = Column(String(255), nullable=True)  # Primary city for zip (from Zippopotam.us or CSV)

    # Re-add after running scripts/migrate_census_schema.py if your table has these columns:
    # total_households, owner_occupied_units, renter_occupied_units,
    # moved_from_different_state, moved_from_different_county, moved_from_abroad, net_migration_yoy

    # Metadata
    data_year = Column(String(4), nullable=False, default='2024')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Index for faster queries
    __table_args__ = (
        Index('idx_zip_year', 'zip_code', 'data_year'),
    )
    
    def to_dict(self):
        """Convert model to dictionary (core fields only for Demographics/map)."""
        return {
            'id': self.id,
            'zip_code': self.zip_code,
            'county': self.county,
            'population': self.population,
            'median_age': self.median_age,
            'average_household_income': self.average_household_income,
            'data_year': self.data_year,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SchoolData(Base):
    """Model for storing school ratings data by address/zip code."""
    
    __tablename__ = 'school_data'
    
    id = Column(Integer, primary_key=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    address = Column(String(255), nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # School ratings (1-10 scale)
    elementary_school_name = Column(String(255), nullable=True)
    elementary_school_rating = Column(Float, nullable=True)
    elementary_school_address = Column(String(255), nullable=True)
    
    middle_school_name = Column(String(255), nullable=True)
    middle_school_rating = Column(Float, nullable=True)
    middle_school_address = Column(String(255), nullable=True)
    
    high_school_name = Column(String(255), nullable=True)
    high_school_rating = Column(Float, nullable=True)
    high_school_address = Column(String(255), nullable=True)
    
    # Blended score (average of all three)
    blended_school_score = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Index for faster queries
    __table_args__ = (
        Index('idx_school_address', 'address'),
        Index('idx_school_zip', 'zip_code'),
        Index('idx_school_location', 'latitude', 'longitude'),  # For fast geographic lookups
        Index('idx_school_ratings', 'elementary_school_rating', 'middle_school_rating', 'high_school_rating'),
    )
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'zip_code': self.zip_code,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'elementary_school_name': self.elementary_school_name,
            'elementary_school_rating': self.elementary_school_rating,
            'elementary_school_address': self.elementary_school_address,
            'middle_school_name': self.middle_school_name,
            'middle_school_rating': self.middle_school_rating,
            'middle_school_address': self.middle_school_address,
            'high_school_name': self.high_school_name,
            'high_school_rating': self.high_school_rating,
            'high_school_address': self.high_school_address,
            'blended_school_score': self.blended_school_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AttendanceZone(Base):
    """Model for storing school attendance zone boundaries."""
    
    __tablename__ = 'attendance_zones'
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey('school_data.id'), nullable=True, index=True)
    
    # School identification
    school_name = Column(String(255), nullable=False, index=True)
    school_level = Column(String(50), nullable=False, index=True)  # 'elementary', 'middle', 'high'
    school_district = Column(String(255), nullable=True, index=True)
    state = Column(String(2), nullable=True, index=True)
    
    # Zone boundary (stored as GeoJSON text)
    zone_boundary = Column(Text, nullable=False)  # GeoJSON polygon
    
    # Metadata
    data_year = Column(String(4), nullable=True)  # Year of zone data
    source = Column(String(100), nullable=True)  # 'NCES', 'district', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_zone_school_level', 'school_name', 'school_level'),
        Index('idx_zone_state', 'state'),
        Index('idx_zone_district', 'school_district'),
    )
    
    def to_dict(self):
        """Convert model to dictionary."""
        import json
        return {
            'id': self.id,
            'school_id': self.school_id,
            'school_name': self.school_name,
            'school_level': self.school_level,
            'school_district': self.school_district,
            'state': self.state,
            'zone_boundary': json.loads(self.zone_boundary) if self.zone_boundary else None,
            'data_year': self.data_year,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class CountyEmployer(Base):
    """Top employers per county (imported from NC statewide dataset)."""

    __tablename__ = 'county_employers'
    __table_args__ = (
        UniqueConstraint('county_name', 'year', 'company_name', 'rank', name='county_employers_unique'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    county_name = Column(String(255), nullable=False, index=True)
    state_code = Column(String(2), nullable=False, default='NC')
    county_fips = Column(String(5), nullable=True, index=True)
    year = Column(Integer, nullable=False, default=2024)
    company_name = Column(String(255), nullable=False)
    industry = Column(String(255), nullable=True)
    sector_class = Column(String(32), nullable=False)  # 'private_sector' or 'public_sector'
    employment_range = Column(String(32), nullable=False)
    rank = Column(Integer, nullable=False)
    avg_salary = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Return a serializable representation for APIs/scripts."""
        return {
            'id': str(self.id) if self.id else None,
            'county_name': self.county_name,
            'state_code': self.state_code,
            'county_fips': self.county_fips,
            'year': self.year,
            'company_name': self.company_name,
            'industry': self.industry,
            'sector_class': self.sector_class,
            'employment_range': self.employment_range,
            'rank': self.rank,
            'avg_salary': self.avg_salary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


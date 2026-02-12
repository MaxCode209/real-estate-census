"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from config.config import Config

# Force Transaction mode (6543) for Supabase pooler - avoid "max clients" on Session mode (5432)
_db_url = Config.DATABASE_URL
if "pooler.supabase.com" in _db_url:
    _db_url = _db_url.replace("pooler.supabase.com:5432", "pooler.supabase.com:6543")
    _db_url = _db_url.replace(".pooler.supabase.com:5432", ".pooler.supabase.com:6543")

# NullPool = no connection pooling: each request gets a new connection and closes it.
# Fits Supabase Transaction mode (6543) and avoids holding connections.
engine = create_engine(
    _db_url,
    echo=False,
    poolclass=NullPool,
    connect_args={"connect_timeout": 15} if "pooler.supabase.com" in _db_url else {},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    from backend.models import CensusData, SchoolData, School, AttendanceZone
    Base.metadata.create_all(bind=engine)


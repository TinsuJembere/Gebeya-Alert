"""
Database configuration and session management.
"""
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator

from config import settings

# Get database URL (handles development vs production)
database_url = settings.get_database_url()

# Detect database type
is_sqlite = database_url.startswith("sqlite")
is_postgresql = database_url.startswith("postgresql") or database_url.startswith("postgres")

# Convert postgresql:// to use explicit driver if needed
# Try psycopg (psycopg3) first, fallback to psycopg2
# SQLAlchemy can auto-detect, but being explicit ensures compatibility
if is_postgresql and "://" in database_url and "+" not in database_url.split("://")[0]:
    # Try psycopg (psycopg3) first - better Windows support
    # Falls back to psycopg2 if psycopg3 not available
    try:
        import psycopg
        # Use psycopg (psycopg3)
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    except ImportError:
        # Fallback to psycopg2
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

if is_sqlite:
    # SQLite configuration: no pooling, check_same_thread=False for async compatibility
    engine = create_engine(
        database_url,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )
elif is_postgresql:
    # PostgreSQL configuration: use connection pooling
    engine = create_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # Recycle connections after 1 hour
    )
else:
    # Fallback for other database types
    engine = create_engine(
        database_url,
        echo=settings.DEBUG,
    )


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a database session and closes it after use.
    """
    session = None
    try:
        session = Session(engine)
        yield session
    except Exception:
        # Rollback on any exception
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Should be called after all models are imported.
    Creates tables if they don't exist, updates schema if needed.
    """
    # Import all models here so they're registered with SQLModel
    from models import User, Crop, Market, Price, Alert, NotificationLog  # noqa: F401
    
    # Create all tables (SQLModel will handle schema updates for new columns)
    # Note: For existing databases, you may need to run migrations or recreate the database
    SQLModel.metadata.create_all(engine)



"""
Database configuration and session management.
"""
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator

from config import settings

# Get database URL (handles development vs production)
database_url = settings.get_database_url()

# SQLite-specific configuration
# SQLite doesn't support connection pooling, so we disable it
is_sqlite = database_url.startswith("sqlite")

if is_sqlite:
    # SQLite configuration: no pooling, check_same_thread=False for async compatibility
    engine = create_engine(
        database_url,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    )
else:
    # PostgreSQL configuration: use connection pooling
    engine = create_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
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



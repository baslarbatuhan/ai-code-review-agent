"""Tests for database connection."""
import pytest
from src.database.connection import get_db, Base, engine
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_database_connection():
    """Test database connection."""
    db = TestingSessionLocal()
    try:
        # Test connection by creating tables
        Base.metadata.create_all(bind=engine)
        assert db is not None
    finally:
        db.close()


def test_get_db_generator():
    """Test get_db dependency generator."""
    db_gen = get_db()
    db = next(db_gen)
    try:
        assert db is not None
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


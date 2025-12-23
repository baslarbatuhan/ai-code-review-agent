"""Error case tests for API routes."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from src.api.main import app
from src.database.connection import get_db, Base, engine
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Set up test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_review_missing_repository_url():
    """Test creating review without repository URL."""
    response = client.post(
        "/api/v1/reviews",
        json={}
    )
    # Should fail validation
    assert response.status_code in [400, 422]


def test_create_review_invalid_json():
    """Test creating review with invalid JSON."""
    response = client.post(
        "/api/v1/reviews",
        json={"invalid": "data"}
    )
    # Should fail validation
    assert response.status_code in [400, 422]


def test_get_review_invalid_id():
    """Test getting review with invalid ID."""
    response = client.get("/api/v1/reviews/abc")  # Not a number
    assert response.status_code in [400, 404, 422]


def test_get_review_negative_id():
    """Test getting review with negative ID."""
    response = client.get("/api/v1/reviews/-1")
    assert response.status_code in [400, 404, 422]


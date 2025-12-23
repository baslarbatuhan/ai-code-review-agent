"""Extended tests for API routes."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.connection import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Review, Repository, ReviewResult

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


def test_get_review_by_id_not_found():
    """Test getting non-existent review."""
    response = client.get("/api/v1/reviews/99999")
    assert response.status_code == 404


def test_create_review_invalid_request():
    """Test creating review with invalid request."""
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "",  # Empty URL
        }
    )
    assert response.status_code in [400, 422]


def test_get_reviews_with_limit():
    """Test getting reviews with limit parameter."""
    response = client.get("/api/v1/reviews?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


def test_get_reviews_with_offset():
    """Test getting reviews with offset parameter."""
    response = client.get("/api/v1/reviews?offset=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_analytics_with_data():
    """Test analytics endpoint returns correct structure."""
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    
    # Check all required fields
    required_fields = [
        "total_reviews", "total_issues", "completed_reviews",
        "success_rate", "avg_issues_per_review",
        "severity_stats", "agent_stats", "repo_stats", "recent_reviews"
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


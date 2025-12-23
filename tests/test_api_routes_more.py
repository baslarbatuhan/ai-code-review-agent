"""More comprehensive API route tests."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
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


def test_get_reviews_pagination():
    """Test getting reviews with pagination parameters."""
    response = client.get("/api/v1/reviews?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_get_reviews_default_limit():
    """Test getting reviews with default limit."""
    response = client.get("/api/v1/reviews")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 50  # Default limit


def test_analytics_empty_database():
    """Test analytics with empty database."""
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    
    # Should return 0 for all metrics when database is empty
    assert data["total_reviews"] == 0
    assert data["total_issues"] == 0
    assert data["success_rate"] == 0


def test_analytics_severity_stats_structure():
    """Test analytics severity stats structure."""
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    
    assert "severity_stats" in data
    assert isinstance(data["severity_stats"], dict)


def test_analytics_agent_stats_structure():
    """Test analytics agent stats structure."""
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    
    assert "agent_stats" in data
    assert isinstance(data["agent_stats"], dict)


def test_analytics_repo_stats_structure():
    """Test analytics repo stats structure."""
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    
    assert "repo_stats" in data
    assert isinstance(data["repo_stats"], list)


def test_delete_reviews_empty():
    """Test deleting reviews when none exist."""
    response = client.delete("/api/v1/reviews")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["deleted_reviews"] == 0
    assert data["deleted_results"] == 0


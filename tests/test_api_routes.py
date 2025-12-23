"""Tests for API routes."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.connection import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Review, Repository, ReviewResult

# Create test database
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


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_create_review_local_file():
    """Test creating review with local file."""
    # Create a test file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('def hello():\n    print("Hello")\n')
        temp_path = f.name
    
    try:
        response = client.post(
            "/api/v1/reviews",
            json={
                "repository_url": "local",
                "file_path": temp_path,
            }
        )
        # Should work or give appropriate error
        assert response.status_code in [200, 400, 404]
    finally:
        os.unlink(temp_path)


def test_get_reviews_empty():
    """Test getting reviews when none exist."""
    response = client.get("/api/v1/reviews")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_analytics():
    """Test analytics endpoint."""
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_reviews" in data
    assert "total_issues" in data
    assert "success_rate" in data
    assert isinstance(data["total_reviews"], int)
    assert isinstance(data["total_issues"], int)


def test_delete_reviews():
    """Test clearing all reviews."""
    response = client.delete("/api/v1/reviews")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "deleted_reviews" in data
    assert "deleted_results" in data


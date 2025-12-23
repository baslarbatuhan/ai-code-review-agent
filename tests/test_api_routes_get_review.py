"""Tests for get review by ID endpoint."""
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


def test_get_review_with_multiple_results():
    """Test getting review with multiple results."""
    db = TestingSessionLocal()
    try:
        # Create repository
        repo = Repository(
            name="test-repo",
            url="https://github.com/test/repo",
            platform="github",
            owner="test"
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)
        
        # Create review
        review = Review(
            repository_id=repo.id,
            file_path="test.py",
            status="completed"
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        
        # Create multiple results
        for i in range(3):
            result = ReviewResult(
                review_id=review.id,
                agent_type="quality",
                severity="low",
                issue_type=f"C011{i}",
                message=f"Issue {i}",
                line_number=i+1
            )
            db.add(result)
        db.commit()
        
        # Test getting review
        response = client.get(f"/api/v1/reviews/{review.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["review_id"] == review.id
        assert len(data["results"]) == 3
    finally:
        db.close()


def test_get_review_different_agent_types():
    """Test getting review with different agent types."""
    db = TestingSessionLocal()
    try:
        repo = Repository(
            name="test-repo",
            url="https://github.com/test/repo",
            platform="github",
            owner="test"
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)
        
        review = Review(
            repository_id=repo.id,
            file_path="test.py",
            status="completed"
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        
        # Create results for different agent types
        agent_types = ["quality", "security", "performance", "documentation"]
        for agent_type in agent_types:
            result = ReviewResult(
                review_id=review.id,
                agent_type=agent_type,
                severity="low",
                issue_type="TEST",
                message=f"{agent_type} issue",
                line_number=1
            )
            db.add(result)
        db.commit()
        
        response = client.get(f"/api/v1/reviews/{review.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 4
    finally:
        db.close()


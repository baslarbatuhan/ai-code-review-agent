"""Tests for analytics endpoint."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.connection import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Review, Repository, ReviewResult
from datetime import datetime, timedelta

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


def test_analytics_with_reviews():
    """Test analytics with actual reviews."""
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
        
        # Create completed review
        review = Review(
            repository_id=repo.id,
            file_path="test.py",
            status="completed",
            completed_at=datetime.utcnow()
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        
        # Create results with different severities
        severities = ["critical", "high", "medium", "low", "info"]
        agent_types = ["quality", "security", "performance", "documentation"]
        
        for i, (severity, agent_type) in enumerate(zip(severities, agent_types)):
            result = ReviewResult(
                review_id=review.id,
                agent_type=agent_type,
                severity=severity,
                issue_type=f"TEST{i}",
                message=f"Test issue {i}",
                line_number=i+1
            )
            db.add(result)
        db.commit()
        
        # Test analytics
        response = client.get("/api/v1/analytics")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_reviews"] >= 1
        assert data["total_issues"] >= 5
        assert data["completed_reviews"] >= 1
        assert "severity_stats" in data
        assert "agent_stats" in data
        assert "repo_stats" in data
    finally:
        db.close()


def test_analytics_recent_reviews():
    """Test analytics with recent reviews."""
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
        
        # Create recent review (within 7 days)
        recent_review = Review(
            repository_id=repo.id,
            file_path="test.py",
            status="completed",
            completed_at=datetime.utcnow() - timedelta(days=3)
        )
        db.add(recent_review)
        db.commit()
        
        # Create old review (more than 7 days ago)
        old_review = Review(
            repository_id=repo.id,
            file_path="old.py",
            status="completed",
            completed_at=datetime.utcnow() - timedelta(days=10)
        )
        db.add(old_review)
        db.commit()
        
        response = client.get("/api/v1/analytics")
        assert response.status_code == 200
        data = response.json()
        
        # Should count recent reviews
        assert data["recent_reviews_count"] >= 1
    finally:
        db.close()


def test_analytics_success_rate():
    """Test analytics success rate calculation."""
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
        
        # Create completed review
        completed_review = Review(
            repository_id=repo.id,
            file_path="test.py",
            status="completed",
            completed_at=datetime.utcnow()
        )
        db.add(completed_review)
        
        # Create pending review
        pending_review = Review(
            repository_id=repo.id,
            file_path="pending.py",
            status="pending"
        )
        db.add(pending_review)
        db.commit()
        
        response = client.get("/api/v1/analytics")
        assert response.status_code == 200
        data = response.json()
        
        # Success rate should be calculated
        assert "success_rate" in data
        assert 0 <= data["success_rate"] <= 100
    finally:
        db.close()


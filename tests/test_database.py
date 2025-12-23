"""Tests for database models and operations."""
import pytest
from datetime import datetime
from src.database.connection import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Review, Repository, ReviewResult

# Create test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Set up test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_repository():
    """Test creating a repository."""
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
        
        assert repo.id is not None
        assert repo.name == "test-repo"
        assert repo.url == "https://github.com/test/repo"
    finally:
        db.close()


def test_create_review():
    """Test creating a review."""
    db = TestingSessionLocal()
    try:
        # First create repository
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
            status="pending"
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        
        assert review.id is not None
        assert review.file_path == "test.py"
        assert review.status == "pending"
    finally:
        db.close()


def test_create_review_result():
    """Test creating a review result."""
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
        
        # Create review result
        result = ReviewResult(
            review_id=review.id,
            agent_type="quality",
            severity="low",
            issue_type="C0114",
            message="Missing module docstring",
            line_number=1,
            suggestion="Add a module-level docstring"
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        assert result.id is not None
        assert result.review_id == review.id
        assert result.agent_type == "quality"
        assert result.severity == "low"
    finally:
        db.close()


def test_repository_relationship():
    """Test repository-review relationship."""
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
            status="pending"
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        
        # Test relationship
        assert review.repository.id == repo.id
        assert len(repo.reviews) == 1
        assert repo.reviews[0].id == review.id
    finally:
        db.close()


def test_review_result_relationship():
    """Test review-result relationship."""
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
        
        result = ReviewResult(
            review_id=review.id,
            agent_type="quality",
            severity="low",
            issue_type="C0114",
            message="Missing module docstring"
        )
        db.add(result)
        db.commit()
        
        # Test relationship
        assert len(review.results) == 1
        assert review.results[0].id == result.id
    finally:
        db.close()


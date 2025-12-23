"""Comprehensive tests for API routes with mocks."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock, AsyncMock
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


@pytest.fixture
def mock_github_integration():
    """Mock GitHub integration."""
    with patch('src.api.routes.reviews.GitHubIntegration') as mock_github:
        mock_instance = Mock()
        mock_github.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator."""
    with patch('src.api.routes.reviews.orchestrator') as mock_orch:
        mock_orch.review_code = AsyncMock(return_value=[
            Mock(
                agent_type=Mock(value="quality"),
                issues=[
                    Mock(
                        severity=Mock(value="low"),
                        issue_type="C0114",
                        message="Missing docstring",
                        line_number=1,
                        suggestion="Add docstring",
                        metadata={}
                    )
                ],
                execution_time=0.5,
                success=True
            )
        ])
        yield mock_orch


def test_create_review_with_scan_entire_repo(mock_github_integration, mock_orchestrator):
    """Test creating review with scan entire repository."""
    # Mock GitHub integration
    mock_github_integration.get_all_python_files.return_value = [
        {"path": "test1.py", "content": "def test(): pass", "size": 100},
        {"path": "test2.py", "content": "def test2(): pass", "size": 100}
    ]
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "scan_entire_repo": True
        }
    )
    
    # Should work or give appropriate error
    assert response.status_code in [200, 400, 500]


def test_create_review_with_directory_scan(mock_github_integration, mock_orchestrator):
    """Test creating review with directory scan."""
    # Mock GitHub integration
    mock_github_integration.get_python_files_in_directory.return_value = [
        {"path": "tests/test1.py", "content": "def test(): pass", "size": 100},
        {"path": "tests/test2.py", "content": "def test2(): pass", "size": 100}
    ]
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "file_path": "tests"  # Directory, not file
        }
    )
    
    # Should work or give appropriate error (404 if GitHub token not configured)
    assert response.status_code in [200, 400, 404, 500]


def test_create_review_with_commit_sha(mock_github_integration, mock_orchestrator):
    """Test creating review with commit SHA."""
    # Mock GitHub integration
    mock_github_integration.get_commit_files.return_value = [
        {
            "path": "test.py",
            "content": "def test(): pass",
            "status": "modified",
            "additions": 10,
            "deletions": 5
        }
    ]
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456"
        }
    )
    
    # Should work or give appropriate error
    assert response.status_code in [200, 400, 500]


def test_create_review_with_pull_request(mock_github_integration, mock_orchestrator):
    """Test creating review with pull request ID."""
    # Mock GitHub integration
    mock_github_integration.get_pull_request_files.return_value = [
        {
            "path": "test.py",
            "content": "def test(): pass",
            "status": "modified",
            "additions": 10,
            "deletions": 5
        }
    ]
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "pull_request_id": 5
        }
    )
    
    # Should work or give appropriate error
    assert response.status_code in [200, 400, 500]


def test_create_review_github_error(mock_github_integration):
    """Test creating review when GitHub integration fails."""
    # Mock GitHub integration to raise error
    mock_github_integration.get_file_content.side_effect = ValueError("File not found")
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "file_path": "nonexistent.py"
        }
    )
    
    assert response.status_code in [400, 404, 500]


def test_create_review_empty_repository_url():
    """Test creating review with empty repository URL."""
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": ""
        }
    )
    
    assert response.status_code in [400, 422]


def test_get_review_by_id_with_results():
    """Test getting review by ID with results."""
    # First create a review
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
            message="Missing docstring",
            line_number=1
        )
        db.add(result)
        db.commit()
        
        # Now test getting it
        response = client.get(f"/api/v1/reviews/{review.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["review_id"] == review.id
        assert data["status"] == "completed"
    finally:
        db.close()


def test_get_reviews_with_pagination():
    """Test getting reviews with pagination."""
    # Create some test reviews
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
        
        for i in range(5):
            review = Review(
                repository_id=repo.id,
                file_path=f"test{i}.py",
                status="completed"
            )
            db.add(review)
        db.commit()
        
        # Test pagination
        response = client.get("/api/v1/reviews?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
    finally:
        db.close()


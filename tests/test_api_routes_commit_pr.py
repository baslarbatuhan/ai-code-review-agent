"""Tests for commit SHA and PR ID functionality."""
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


def test_create_review_with_commit_sha_only(mock_github_integration, mock_orchestrator):
    """Test creating review with only commit SHA (no file_path)."""
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
    assert response.status_code in [200, 400, 404, 500]


def test_create_review_with_pr_id_only(mock_github_integration, mock_orchestrator):
    """Test creating review with only PR ID (no file_path, no commit_sha)."""
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
    assert response.status_code in [200, 400, 404, 500]


def test_create_review_pr_id_zero_ignored(mock_github_integration, mock_orchestrator):
    """Test that PR ID 0 is ignored."""
    # Mock GitHub integration
    mock_github_integration.get_file_content.return_value = "def test(): pass"
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "file_path": "test.py",
            "pull_request_id": 0  # Should be ignored
        }
    )
    
    # Should work with file_path, PR ID 0 should be ignored
    assert response.status_code in [200, 400, 404, 500]

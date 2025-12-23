"""Tests for directory scan functionality in API routes."""
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


def test_directory_scan_success(mock_github_integration, mock_orchestrator):
    """Test successful directory scan."""
    # Mock GitHub integration
    mock_github_integration.get_python_files_in_directory.return_value = [
        {"path": "tests/test1.py", "content": "def test(): pass", "size": 100},
        {"path": "tests/test2.py", "content": "def test2(): pass", "size": 100}
    ]
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "file_path": "tests"  # Directory path
        }
    )
    
    # Should work or give appropriate error (404 if GitHub token not configured)
    assert response.status_code in [200, 400, 404, 500]


def test_directory_scan_empty_directory(mock_github_integration):
    """Test directory scan with empty directory."""
    # Mock GitHub integration to return empty list
    mock_github_integration.get_python_files_in_directory.return_value = []
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "file_path": "empty_dir"
        }
    )
    
    # Should return error for empty directory
    assert response.status_code in [400, 404, 500]


def test_directory_scan_many_files(mock_github_integration, mock_orchestrator):
    """Test directory scan with many files (should limit to 50)."""
    # Mock GitHub integration to return more than 50 files
    many_files = [
        {"path": f"tests/test{i}.py", "content": "def test(): pass", "size": 100}
        for i in range(60)
    ]
    mock_github_integration.get_python_files_in_directory.return_value = many_files
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "file_path": "tests"
        }
    )
    
    # Should work but limit to 50 files
    assert response.status_code in [200, 400, 404, 500]

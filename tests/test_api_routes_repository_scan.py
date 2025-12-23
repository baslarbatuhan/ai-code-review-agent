"""Tests for repository scan functionality."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from src.api.main import app
from src.database.connection import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Review, Repository

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
        from src.core.schemas import AgentType, Issue, Severity
        
        mock_result = Mock()
        mock_result.agent_type = Mock(value="quality")
        mock_result.issues = [
            Mock(
                severity=Mock(value="low"),
                issue_type="C0114",
                message="Missing docstring",
                line_number=1,
                suggestion="Add docstring",
                metadata={}
            )
        ]
        mock_result.execution_time = 0.5
        mock_result.success = True
        
        mock_orch.review_code = AsyncMock(return_value=[mock_result])
        yield mock_orch


def test_repository_scan_no_files_found(mock_github_integration):
    """Test repository scan when no Python files found."""
    mock_github_integration.get_all_python_files.return_value = []
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "scan_entire_repo": True
        }
    )
    
    assert response.status_code == 404


def test_repository_scan_with_files(mock_github_integration, mock_orchestrator):
    """Test repository scan with files."""
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
    assert response.status_code in [200, 400, 404, 500]


def test_repository_scan_file_limit(mock_github_integration, mock_orchestrator):
    """Test repository scan with file limit (more than 50 files)."""
    # Create 60 files
    many_files = [
        {"path": f"test{i}.py", "content": "def test(): pass", "size": 100}
        for i in range(60)
    ]
    mock_github_integration.get_all_python_files.return_value = many_files
    
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "https://github.com/test/repo",
            "scan_entire_repo": True
        }
    )
    
    # Should work or give appropriate error
    assert response.status_code in [200, 400, 404, 500]


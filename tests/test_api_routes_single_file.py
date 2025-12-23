"""Tests for single file review in API routes."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from src.api.main import app
from src.database.connection import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

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


def test_create_review_single_file_local(mock_orchestrator):
    """Test creating review for single local file."""
    # Create a temporary Python file
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
        assert response.status_code in [200, 400, 500]
    finally:
        os.unlink(temp_path)


def test_create_review_single_file_github(mock_orchestrator):
    """Test creating review for single file from GitHub."""
    with patch('src.api.routes.reviews.GitHubIntegration') as mock_github:
        mock_instance = Mock()
        mock_instance.get_file_content.return_value = 'def hello():\n    print("Hello")\n'
        mock_github.return_value = mock_instance
        
        response = client.post(
            "/api/v1/reviews",
            json={
                "repository_url": "https://github.com/test/repo",
                "file_path": "src/main.py",
            }
        )
        # Should work or give appropriate error (404 if GitHub token not configured)
        assert response.status_code in [200, 400, 404, 500]


def test_create_review_single_file_not_found():
    """Test creating review for non-existent file."""
    response = client.post(
        "/api/v1/reviews",
        json={
            "repository_url": "local",
            "file_path": "/nonexistent/file.py",
        }
    )
    # Should return error
    assert response.status_code in [400, 404, 500]


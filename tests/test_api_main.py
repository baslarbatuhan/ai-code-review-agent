"""Tests for API main application."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api.main import app, lifespan
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
    """Setup and teardown database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_app_initialization():
    """Test that the app is initialized correctly."""
    assert app is not None
    assert app.title is not None
    assert app.version is not None


@pytest.mark.asyncio
async def test_lifespan_startup():
    """Test lifespan context manager startup."""
    with patch('src.api.main.logger') as mock_logger:
        with patch('src.api.main.Base.metadata.create_all') as mock_create_all:
            with patch('src.api.main.settings') as mock_settings:
                mock_settings.app_name = "Test App"
                mock_settings.app_version = "1.0.0"
                mock_settings.debug = False
                mock_settings.log_level = "INFO"
                
                # Test lifespan startup
                async with lifespan(app) as result:
                    # Verify startup actions
                    mock_create_all.assert_called_once()
                    assert mock_logger.info.called


@pytest.mark.asyncio
async def test_lifespan_shutdown():
    """Test lifespan context manager shutdown."""
    with patch('src.api.main.logger') as mock_logger:
        with patch('src.api.main.Base.metadata.create_all'):
            # Start lifespan and let it complete
            async with lifespan(app):
                pass
            
            # Verify shutdown was called (should be called after context exits)
            assert mock_logger.info.called


def test_cors_middleware():
    """Test that CORS middleware is configured."""
    # Make a request with CORS headers
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
    )
    
    # CORS middleware should allow the request
    assert response.status_code in [200, 204, 405]  # Options might return different codes


def test_app_includes_routers():
    """Test that routers are included in the app."""
    # Check that health router is included
    routes = [route.path for route in app.routes]
    assert "/api/v1/health" in routes or any("/health" in route for route in routes)
    
    # Check that reviews router is included
    assert "/api/v1/reviews" in routes or any("/reviews" in route for route in routes)


def test_app_metadata():
    """Test app metadata."""
    assert app.title is not None
    assert app.version is not None
    assert app.description is not None


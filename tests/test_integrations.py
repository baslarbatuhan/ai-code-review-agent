"""Tests for external integrations."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.integrations.github import GitHubIntegration
from src.integrations.llm import LLMIntegration


def test_github_integration_init_no_token():
    """Test GitHub integration initialization without token."""
    with patch('src.integrations.github.settings') as mock_settings:
        mock_settings.github_token = None
        integration = GitHubIntegration()
        assert integration.github is None


def test_github_integration_init_with_token():
    """Test GitHub integration initialization with token."""
    with patch('src.integrations.github.settings') as mock_settings:
        mock_settings.github_token = "test_token"
        with patch('src.integrations.github.Github') as mock_github:
            integration = GitHubIntegration()
            mock_github.assert_called_once_with("test_token")


@patch('src.integrations.github.Github')
def test_github_get_repository_from_url(mock_github_class):
    """Test getting repository from URL."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    integration = GitHubIntegration(token="test_token")
    repo = integration.get_repository("https://github.com/owner/repo")
    
    mock_github.get_repo.assert_called_once_with("owner/repo")
    assert repo == mock_repo


def test_llm_integration_init():
    """Test LLM integration initialization."""
    with patch('src.integrations.llm.settings') as mock_settings:
        mock_settings.llm_provider = "ollama"
        integration = LLMIntegration()
        assert integration.provider == "ollama"


@pytest.mark.asyncio
async def test_llm_analyze_code_no_llm():
    """Test LLM analyze when LLM not available."""
    with patch('src.integrations.llm.LANGCHAIN_AVAILABLE', False):
        integration = LLMIntegration()
        result = await integration.analyze_code("def test(): pass", "test.py")
        
        assert "success" in result
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)
        # When LLM not available, it returns success=False
        assert result.get("success") is False or "issues" in result


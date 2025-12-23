"""Extended tests for integrations."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.integrations.github import GitHubIntegration


@patch('src.integrations.github.Github')
def test_github_get_repository_short_url(mock_github_class):
    """Test getting repository from short URL format."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    integration = GitHubIntegration(token="test_token")
    repo = integration.get_repository("owner/repo")
    
    mock_github.get_repo.assert_called_once_with("owner/repo")
    assert repo == mock_repo


@patch('src.integrations.github.Github')
def test_github_get_repository_with_git_suffix(mock_github_class):
    """Test getting repository from URL with .git suffix."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    integration = GitHubIntegration(token="test_token")
    repo = integration.get_repository("https://github.com/owner/repo.git")
    
    mock_github.get_repo.assert_called_once_with("owner/repo")
    assert repo == mock_repo


def test_github_integration_invalid_url():
    """Test GitHub integration with invalid URL."""
    with patch('src.integrations.github.settings') as mock_settings:
        mock_settings.github_token = "test_token"
        with patch('src.integrations.github.Github') as mock_github_class:
            mock_github = Mock()
            mock_github_class.return_value = mock_github
            mock_github.get_repo.side_effect = Exception("Invalid URL")
            
            integration = GitHubIntegration()
            with pytest.raises(Exception):
                integration.get_repository("invalid-url")


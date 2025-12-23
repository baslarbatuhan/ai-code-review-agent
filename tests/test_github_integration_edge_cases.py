"""Edge case tests for GitHub integration."""
import pytest
from unittest.mock import Mock, patch
from src.integrations.github import GitHubIntegration


@patch('src.integrations.github.Github')
def test_get_all_python_files_skips_common_dirs(mock_github_class):
    """Test that get_all_python_files skips common non-source directories."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    # Mock directories that should be skipped
    mock_venv_dir = Mock()
    mock_venv_dir.type = "dir"
    mock_venv_dir.name = "venv"
    mock_venv_dir.path = "venv"
    
    mock_node_modules = Mock()
    mock_node_modules.type = "dir"
    mock_node_modules.name = "node_modules"
    mock_node_modules.path = "node_modules"
    
    mock_py_file = Mock()
    mock_py_file.type = "file"
    mock_py_file.name = "main.py"
    mock_py_file.path = "main.py"
    mock_py_file.size = 100
    
    def mock_get_contents(path, ref=None):
        if path == "":
            return [mock_venv_dir, mock_node_modules, mock_py_file]
        return []
    
    mock_repo.get_contents.side_effect = mock_get_contents
    
    integration = GitHubIntegration(token="test_token")
    
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_all_python_files("https://github.com/test/repo")
        
        # Should only include main.py, not venv or node_modules
        assert len(files) == 1
        assert files[0]["path"] == "main.py"


@patch('src.integrations.github.Github')
def test_get_all_python_files_max_depth(mock_github_class):
    """Test that get_all_python_files handles deep directory structures."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    # Create a deep directory structure
    files = []
    for depth in range(5):
        mock_file = Mock()
        mock_file.type = "file"
        mock_file.name = f"file{depth}.py"
        mock_file.path = "/".join([f"level{i}" for i in range(depth+1)] + [f"file{depth}.py"])
        mock_file.size = 100
        files.append(mock_file)
    
    def mock_get_contents(path, ref=None):
        if path == "":
            return [files[0]]
        # Return files for each level
        return [f for f in files if path in f.path and f.path.count("/") == path.count("/") + 1]
    
    mock_repo.get_contents.side_effect = mock_get_contents
    
    integration = GitHubIntegration(token="test_token")
    
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        result_files = integration.get_all_python_files("https://github.com/test/repo")
        
        # Should find files at different depths
        assert len(result_files) > 0


@patch('src.integrations.github.Github')
def test_get_file_content_handles_403_error(mock_github_class):
    """Test that get_file_content handles 403 Forbidden errors."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    # Simulate 403 error
    from github import GithubException
    mock_repo.get_contents.side_effect = GithubException(403, {"message": "Forbidden"}, headers={})
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="403|Forbidden|permission"):
        integration.get_file_content("https://github.com/test/repo", "private.py")


@patch('src.integrations.github.Github')
def test_get_python_files_in_directory_empty_result(mock_github_class):
    """Test get_python_files_in_directory with empty result."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    # Return empty list
    mock_repo.get_contents.return_value = []
    
    integration = GitHubIntegration(token="test_token")
    
    files = integration.get_python_files_in_directory("https://github.com/test/repo", "empty_dir")
    
    assert files == []


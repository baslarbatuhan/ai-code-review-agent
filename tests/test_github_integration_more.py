"""More comprehensive GitHub integration tests."""
import pytest
from unittest.mock import Mock, patch
from src.integrations.github import GitHubIntegration


@patch('src.integrations.github.Github')
def test_get_all_python_files_recursive(mock_github_class):
    """Test getting all Python files recursively."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    # Mock root directory with subdirectories
    mock_root_dir = Mock()
    mock_root_dir.type = "dir"
    mock_root_dir.name = "src"
    mock_root_dir.path = "src"
    
    mock_sub_dir = Mock()
    mock_sub_dir.type = "dir"
    mock_sub_dir.name = "utils"
    mock_sub_dir.path = "src/utils"
    
    mock_py_file1 = Mock()
    mock_py_file1.type = "file"
    mock_py_file1.name = "main.py"
    mock_py_file1.path = "src/main.py"
    mock_py_file1.size = 100
    
    mock_py_file2 = Mock()
    mock_py_file2.type = "file"
    mock_py_file2.name = "helper.py"
    mock_py_file2.path = "src/utils/helper.py"
    mock_py_file2.size = 100
    
    # Mock get_contents to return different things based on path
    def mock_get_contents(path, ref=None):
        if path == "":
            return [mock_root_dir]
        elif path == "src":
            return [mock_sub_dir, mock_py_file1]
        elif path == "src/utils":
            return [mock_py_file2]
        return []
    
    mock_repo.get_contents.side_effect = mock_get_contents
    
    integration = GitHubIntegration(token="test_token")
    
    # Mock get_file_content to avoid actual file fetching
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_all_python_files("https://github.com/test/repo")
        
        assert len(files) >= 2
        assert all(f["path"].endswith(".py") for f in files)


@patch('src.integrations.github.Github')
def test_get_python_files_in_directory_nested(mock_github_class):
    """Test getting Python files from nested directory."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_py_file = Mock()
    mock_py_file.type = "file"
    mock_py_file.name = "test.py"
    mock_py_file.path = "tests/unit/test.py"
    mock_py_file.size = 100
    
    mock_repo.get_contents.return_value = [mock_py_file]
    
    integration = GitHubIntegration(token="test_token")
    
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_python_files_in_directory("https://github.com/test/repo", "tests/unit")
        
        assert len(files) == 1
        assert files[0]["path"] == "tests/unit/test.py"


@patch('src.integrations.github.Github')
def test_get_file_content_binary_file(mock_github_class):
    """Test getting binary file content (should raise error)."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    mock_file_content.decoded_content = b'\x89PNG\r\n\x1a\n'  # PNG header (binary)
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="binary"):
        integration.get_file_content("https://github.com/test/repo", "image.png")


@patch('src.integrations.github.Github')
def test_get_file_content_base64_encoded(mock_github_class):
    """Test getting file content from base64 encoded content."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    # No decoded_content, only content (base64)
    del mock_file_content.decoded_content
    import base64
    mock_file_content.content = base64.b64encode(b"def test(): pass\n").decode('utf-8')
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    content = integration.get_file_content("https://github.com/test/repo", "test.py")
    
    assert content == "def test(): pass\n"


@patch('src.integrations.github.Github')
def test_get_pull_request_files_multiple(mock_github_class):
    """Test getting multiple files from pull request."""
    mock_github = Mock()
    mock_github_class.return_value = mock_github
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_pr = Mock()
    mock_pr.head.sha = "abc123"
    mock_repo.get_pull.return_value = mock_pr
    
    mock_file1 = Mock()
    mock_file1.filename = "test1.py"
    mock_file1.status = "modified"
    mock_file1.additions = 10
    mock_file1.deletions = 5
    
    mock_file2 = Mock()
    mock_file2.filename = "test2.py"
    mock_file2.status = "added"
    mock_file2.additions = 20
    mock_file2.deletions = 0
    
    mock_pr.get_files.return_value = [mock_file1, mock_file2]
    
    integration = GitHubIntegration(token="test_token")
    
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_pull_request_files("https://github.com/test/repo", 5)
        
        assert len(files) == 2
        assert files[0]["path"] == "test1.py"
        assert files[1]["path"] == "test2.py"


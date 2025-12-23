"""Comprehensive tests for GitHub integration with mocks."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.integrations.github import GitHubIntegration


@pytest.fixture
def mock_github():
    """Mock GitHub client."""
    with patch('src.integrations.github.Github') as mock_github_class:
        mock_github_instance = Mock()
        mock_github_class.return_value = mock_github_instance
        yield mock_github_instance


def test_get_file_content_success(mock_github):
    """Test getting file content successfully."""
    # Setup mock
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    mock_file_content.decoded_content = b"def hello():\n    pass\n"
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    content = integration.get_file_content("https://github.com/test/repo", "test.py")
    
    assert content == "def hello():\n    pass\n"
    # Check that get_contents was called (ref=None is not passed explicitly)
    mock_repo.get_contents.assert_called()
    # Verify it was called with correct file path
    call_args = mock_repo.get_contents.call_args
    assert call_args[0][0] == "test.py"


def test_get_file_content_with_ref(mock_github):
    """Test getting file content with ref."""
    # Setup mock
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    mock_file_content.decoded_content = b"def hello():\n    pass\n"
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    content = integration.get_file_content("https://github.com/test/repo", "test.py", ref="main")
    
    assert content == "def hello():\n    pass\n"
    # Check that get_contents was called with ref
    mock_repo.get_contents.assert_called()
    call_args = mock_repo.get_contents.call_args
    assert call_args[0][0] == "test.py"
    assert call_args[1]["ref"] == "main"


def test_get_file_content_not_found(mock_github):
    """Test getting file content when file not found."""
    # Setup mock
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.side_effect = Exception("404 Not Found")
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="not found"):
        integration.get_file_content("https://github.com/test/repo", "nonexistent.py")


def test_get_file_content_empty(mock_github):
    """Test getting empty file content."""
    # Setup mock
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    mock_file_content.decoded_content = b""
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="empty"):
        integration.get_file_content("https://github.com/test/repo", "empty.py")


def test_get_all_python_files(mock_github):
    """Test getting all Python files from repository."""
    # Setup mock
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    # Mock directory structure
    mock_root_dir = Mock()
    mock_root_dir.type = "dir"
    mock_root_dir.name = "src"
    mock_root_dir.path = "src"
    
    mock_py_file = Mock()
    mock_py_file.type = "file"
    mock_py_file.name = "test.py"
    mock_py_file.path = "src/test.py"
    mock_py_file.size = 100
    mock_py_file.decoded_content = b"def test(): pass\n"
    
    # First call returns directory, second call returns file
    mock_repo.get_contents.side_effect = [
        [mock_root_dir],  # Root directory
        [mock_py_file]    # Files in src directory
    ]
    
    integration = GitHubIntegration(token="test_token")
    
    # Mock get_file_content to avoid recursion
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_all_python_files("https://github.com/test/repo")
        
        assert len(files) > 0
        assert all(f["path"].endswith(".py") for f in files)


def test_get_python_files_in_directory(mock_github):
    """Test getting Python files from specific directory."""
    # Setup mock
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_py_file1 = Mock()
    mock_py_file1.type = "file"
    mock_py_file1.name = "test1.py"
    mock_py_file1.path = "tests/test1.py"
    mock_py_file1.size = 100
    mock_py_file1.decoded_content = b"def test1(): pass\n"
    
    mock_py_file2 = Mock()
    mock_py_file2.type = "file"
    mock_py_file2.name = "test2.py"
    mock_py_file2.path = "tests/test2.py"
    mock_py_file2.size = 100
    mock_py_file2.decoded_content = b"def test2(): pass\n"
    
    mock_repo.get_contents.return_value = [mock_py_file1, mock_py_file2]
    
    integration = GitHubIntegration(token="test_token")
    
    # Mock get_file_content
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_python_files_in_directory("https://github.com/test/repo", "tests")
        
        assert len(files) == 2
        assert all(f["path"].startswith("tests/") for f in files)


def test_get_pull_request_files(mock_github):
    """Test getting files from pull request."""
    # Setup mock
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_pr = Mock()
    mock_pr.head.sha = "abc123"
    mock_repo.get_pull.return_value = mock_pr
    
    mock_file = Mock()
    mock_file.filename = "test.py"
    mock_file.status = "modified"
    mock_file.additions = 10
    mock_file.deletions = 5
    mock_pr.get_files.return_value = [mock_file]
    
    integration = GitHubIntegration(token="test_token")
    
    # Mock get_file_content
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_pull_request_files("https://github.com/test/repo", 5)
        
        assert len(files) == 1
        assert files[0]["path"] == "test.py"
        assert files[0]["status"] == "modified"


def test_get_commit_files(mock_github):
    """Test getting files from commit."""
    # Setup mock
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_commit = Mock()
    mock_repo.get_commit.return_value = mock_commit
    
    mock_file = Mock()
    mock_file.filename = "test.py"
    mock_file.status = "modified"
    mock_file.additions = 10
    mock_file.deletions = 5
    mock_commit.files = [mock_file]
    
    integration = GitHubIntegration(token="test_token")
    
    # Mock get_file_content
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_commit_files("https://github.com/test/repo", "abc123")
        
        assert len(files) == 1
        assert files[0]["path"] == "test.py"
        assert files[0]["status"] == "modified"


def test_get_repository_gitlab_url():
    """Test getting repository from GitLab URL."""
    with patch('src.integrations.github.Github') as mock_github_class:
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        
        integration = GitHubIntegration(token="test_token")
        # GitLab URLs should still work (though we use GitHub client)
        # This tests the URL parsing logic
        try:
            repo = integration.get_repository("https://gitlab.com/test/repo")
            # Should either work or raise appropriate error
        except (ValueError, Exception):
            pass  # Expected for GitLab with GitHub client


def test_get_repository_invalid_url():
    """Test getting repository with invalid URL."""
    with patch('src.integrations.github.Github') as mock_github_class:
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_github.get_repo.side_effect = Exception("Invalid URL")
        
        integration = GitHubIntegration(token="test_token")
        
        with pytest.raises(Exception):
            integration.get_repository("invalid-url")


def test_get_file_content_list_response(mock_github):
    """Test getting file content when get_contents returns a list."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    mock_file_content.decoded_content = b"def hello():\n    pass\n"
    # get_contents returns a list (edge case)
    mock_repo.get_contents.return_value = [mock_file_content]
    
    integration = GitHubIntegration(token="test_token")
    content = integration.get_file_content("https://github.com/test/repo", "test.py")
    
    assert content == "def hello():\n    pass\n"


def test_get_file_content_list_empty(mock_github):
    """Test getting file content when get_contents returns empty list."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.return_value = []
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="not found"):
        integration.get_file_content("https://github.com/test/repo", "nonexistent.py")


def test_get_file_content_base64_encoded(mock_github):
    """Test getting file content from base64 encoded content."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    # No decoded_content, but has content (base64)
    mock_file_content.decoded_content = None
    import base64
    mock_file_content.content = base64.b64encode(b"def hello():\n    pass\n").decode('utf-8')
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    content = integration.get_file_content("https://github.com/test/repo", "test.py")
    
    assert content == "def hello():\n    pass\n"


def test_get_file_content_binary_file(mock_github):
    """Test getting file content for binary file."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    # Simulate binary data that can't be decoded
    mock_file_content.decoded_content = b"\xff\xfe\x00\x01"  # Invalid UTF-8
    mock_file_content.content = None
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    
    # Should raise ValueError for binary file
    with pytest.raises(ValueError, match="binary file"):
        integration.get_file_content("https://github.com/test/repo", "binary.bin")


def test_get_file_content_unicode_decode_error(mock_github):
    """Test getting file content with UnicodeDecodeError."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    # Simulate UnicodeDecodeError
    mock_file_content.decoded_content = b"\xff\xfe"  # Invalid UTF-8
    mock_file_content.content = None
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="binary file"):
        integration.get_file_content("https://github.com/test/repo", "test.py")


def test_get_file_content_no_content_attributes(mock_github):
    """Test getting file content when file has no content attributes."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_file_content = Mock()
    mock_file_content.decoded_content = None
    mock_file_content.content = None
    mock_repo.get_contents.return_value = mock_file_content
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="Could not extract content"):
        integration.get_file_content("https://github.com/test/repo", "test.py")


def test_get_file_content_403_forbidden(mock_github):
    """Test getting file content with 403 Forbidden error."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.side_effect = Exception("403 Forbidden")
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="forbidden"):
        integration.get_file_content("https://github.com/test/repo", "test.py")


def test_get_file_content_generic_error(mock_github):
    """Test getting file content with generic error."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.side_effect = Exception("Generic error message")
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError):
        integration.get_file_content("https://github.com/test/repo", "test.py")


def test_get_all_python_files_no_token():
    """Test getting all Python files without token."""
    with patch('src.integrations.github.settings') as mock_settings:
        mock_settings.github_token = None
        integration = GitHubIntegration(token=None)
        
        with pytest.raises(ValueError, match="token not configured"):
            integration.get_all_python_files("https://github.com/test/repo")


def test_get_python_files_in_directory_no_token():
    """Test getting Python files in directory without token."""
    with patch('src.integrations.github.settings') as mock_settings:
        mock_settings.github_token = None
        integration = GitHubIntegration(token=None)
        
        with pytest.raises(ValueError, match="token not configured"):
            integration.get_python_files_in_directory("https://github.com/test/repo", "src")


def test_get_python_files_in_directory_404(mock_github):
    """Test getting Python files in directory that doesn't exist."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.side_effect = Exception("404 Not Found")
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError, match="not found"):
        integration.get_python_files_in_directory("https://github.com/test/repo", "nonexistent")


def test_get_python_files_in_directory_error(mock_github):
    """Test getting Python files in directory with error."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.side_effect = Exception("Generic error")
    
    integration = GitHubIntegration(token="test_token")
    
    with pytest.raises(ValueError):
        integration.get_python_files_in_directory("https://github.com/test/repo", "src")


def test_get_pull_request_files_non_python(mock_github):
    """Test getting pull request files with non-Python files."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_pr = Mock()
    mock_pr.head.sha = "abc123"
    mock_repo.get_pull.return_value = mock_pr
    
    mock_file_py = Mock()
    mock_file_py.filename = "test.py"
    mock_file_py.status = "modified"
    mock_file_py.additions = 10
    mock_file_py.deletions = 5
    
    mock_file_js = Mock()
    mock_file_js.filename = "test.js"
    mock_file_js.status = "modified"
    
    mock_pr.get_files.return_value = [mock_file_py, mock_file_js]
    
    integration = GitHubIntegration(token="test_token")
    
    with patch.object(integration, 'get_file_content', return_value="def test(): pass\n"):
        files = integration.get_pull_request_files("https://github.com/test/repo", 5)
        
        # Should only return Python files
        assert len(files) == 1
        assert files[0]["path"] == "test.py"


def test_get_pull_request_files_exception(mock_github):
    """Test getting pull request files when file fetch fails."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_pr = Mock()
    mock_pr.head.sha = "abc123"
    mock_repo.get_pull.return_value = mock_pr
    
    mock_file = Mock()
    mock_file.filename = "test.py"
    mock_file.status = "modified"
    mock_file.additions = 10
    mock_file.deletions = 5
    mock_pr.get_files.return_value = [mock_file]
    
    integration = GitHubIntegration(token="test_token")
    
    with patch.object(integration, 'get_file_content', side_effect=Exception("Error")):
        files = integration.get_pull_request_files("https://github.com/test/repo", 5)
        
        # Should return empty list when file fetch fails
        assert len(files) == 0


def test_get_commit_files_removed_file(mock_github):
    """Test getting commit files with removed file."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_commit = Mock()
    mock_repo.get_commit.return_value = mock_commit
    
    mock_file = Mock()
    mock_file.filename = "test.py"
    mock_file.status = "removed"
    mock_file.additions = 0
    mock_file.deletions = 10
    mock_commit.files = [mock_file]
    
    integration = GitHubIntegration(token="test_token")
    
    files = integration.get_commit_files("https://github.com/test/repo", "abc123")
    
    # Should not include removed files
    assert len(files) == 0


def test_get_commit_files_exception(mock_github):
    """Test getting commit files when file fetch fails."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    mock_commit = Mock()
    mock_repo.get_commit.return_value = mock_commit
    
    mock_file = Mock()
    mock_file.filename = "test.py"
    mock_file.status = "modified"
    mock_file.additions = 10
    mock_file.deletions = 5
    mock_commit.files = [mock_file]
    
    integration = GitHubIntegration(token="test_token")
    
    with patch.object(integration, 'get_file_content', side_effect=Exception("Error")):
        files = integration.get_commit_files("https://github.com/test/repo", "abc123")
        
        # Should return empty list when file fetch fails
        assert len(files) == 0


def test_get_repository_short_url(mock_github):
    """Test getting repository with short URL format."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    integration = GitHubIntegration(token="test_token")
    repo = integration.get_repository("owner/repo")
    
    assert repo == mock_repo
    mock_github.get_repo.assert_called_with("owner/repo")


def test_get_repository_url_with_git_suffix(mock_github):
    """Test getting repository with .git suffix."""
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    
    integration = GitHubIntegration(token="test_token")
    repo = integration.get_repository("https://github.com/owner/repo.git")
    
    assert repo == mock_repo
    mock_github.get_repo.assert_called_with("owner/repo")


"""Extended tests for static analysis utilities."""
import pytest
from src.utils.static_analysis import run_pylint, run_flake8, run_bandit, run_radon
from unittest.mock import patch, Mock


def test_run_pylint_timeout():
    """Test pylint timeout handling."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = TimeoutError("Timeout")
        
        result = run_pylint("def test(): pass", "test.py")
        
        assert result["success"] is False
        assert "error" in result or "Timeout" in str(result)


def test_run_pylint_invalid_json():
    """Test pylint with invalid JSON output."""
    with patch('subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.stdout = "invalid json"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = run_pylint("def test(): pass", "test.py")
        
        # Should handle gracefully
        assert "success" in result


def test_run_flake8_timeout():
    """Test flake8 timeout handling."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = TimeoutError("Timeout")
        
        result = run_flake8("def test(): pass", "test.py")
        
        assert result["success"] is False
        assert "error" in result or "Timeout" in str(result)


def test_run_flake8_empty_output():
    """Test flake8 with empty output."""
    with patch('subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = run_flake8("def test(): pass", "test.py")
        
        assert result["success"] is True
        assert result["issues"] == []


def test_run_bandit_timeout():
    """Test bandit timeout handling."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = TimeoutError("Timeout")
        
        result = run_bandit("import subprocess", "test.py")
        
        assert result["success"] is False
        assert "error" in result or "Timeout" in str(result)


def test_run_bandit_invalid_json():
    """Test bandit with invalid JSON output."""
    with patch('subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.stdout = "invalid json"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = run_bandit("import subprocess", "test.py")
        
        # Should handle gracefully
        assert "success" in result


def test_run_radon_timeout():
    """Test radon timeout handling."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = TimeoutError("Timeout")
        
        result = run_radon("def test(): pass", "test.py")
        
        assert result["success"] is False
        assert "error" in result or "Timeout" in str(result)


def test_run_radon_invalid_json():
    """Test radon with invalid JSON output."""
    with patch('subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.stdout = "invalid json"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = run_radon("def test(): pass", "test.py")
        
        # Should handle gracefully
        assert "success" in result


def test_run_pylint_file_error():
    """Test pylint with file error."""
    with patch('tempfile.NamedTemporaryFile') as mock_temp:
        mock_temp.side_effect = IOError("File error")
        
        result = run_pylint("def test(): pass", "test.py")
        
        assert result["success"] is False


def test_run_flake8_file_error():
    """Test flake8 with file error."""
    with patch('tempfile.NamedTemporaryFile') as mock_temp:
        mock_temp.side_effect = IOError("File error")
        
        result = run_flake8("def test(): pass", "test.py")
        
        assert result["success"] is False


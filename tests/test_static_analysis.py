"""Tests for static analysis utilities."""
import pytest
from src.utils.static_analysis import run_pylint, run_flake8, run_bandit, run_radon


def test_run_pylint():
    """Test pylint execution."""
    code = '''
def hello():
    print("Hello")
'''
    result = run_pylint(code, "test.py")
    
    assert "success" in result
    assert isinstance(result["success"], bool)
    assert "issues" in result
    assert isinstance(result["issues"], list)


def test_run_flake8():
    """Test flake8 execution."""
    code = '''
def hello():
    print("Hello")
'''
    result = run_flake8(code, "test.py")
    
    assert "success" in result
    assert isinstance(result["success"], bool)
    assert "issues" in result
    assert isinstance(result["issues"], list)


def test_run_bandit():
    """Test bandit execution."""
    code = '''
import subprocess
subprocess.call("ls")
'''
    result = run_bandit(code, "test.py")
    
    assert "success" in result
    assert isinstance(result["success"], bool)
    assert "issues" in result
    assert isinstance(result["issues"], list)


def test_run_radon():
    """Test radon execution."""
    code = '''
def simple_function():
    return 42
'''
    result = run_radon(code, "test.py")
    
    assert "success" in result
    assert isinstance(result["success"], bool)


def test_run_pylint_with_errors():
    """Test pylint with code containing errors."""
    code = '''
def hello(
    print("Hello")
'''
    result = run_pylint(code, "test.py")
    
    # Should handle syntax errors gracefully
    assert "success" in result


def test_run_flake8_with_style_issues():
    """Test flake8 with style issues."""
    code = '''
def hello():
    x=1+2
    print(x)
'''
    result = run_flake8(code, "test.py")
    
    assert "success" in result
    assert isinstance(result["issues"], list)


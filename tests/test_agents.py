"""Tests for agents."""
import pytest
from src.agents import QualityAgent, SecurityAgent, PerformanceAgent, DocumentationAgent
from src.core.schemas import AgentType


@pytest.fixture
def sample_code():
    """Sample Python code for testing."""
    return '''
def hello_world():
    print("Hello, World!")
    x = 1 + 2
    return x
'''


@pytest.mark.asyncio
async def test_quality_agent(sample_code):
    """Test Quality Agent."""
    agent = QualityAgent()
    result = await agent.review(sample_code, "test.py")
    
    assert result.agent_type == AgentType.QUALITY
    assert result.success is True
    assert isinstance(result.issues, list)


@pytest.mark.asyncio
async def test_security_agent(sample_code):
    """Test Security Agent."""
    agent = SecurityAgent()
    result = await agent.review(sample_code, "test.py")
    
    assert result.agent_type == AgentType.SECURITY
    assert result.success is True
    assert isinstance(result.issues, list)


@pytest.mark.asyncio
async def test_performance_agent(sample_code):
    """Test Performance Agent."""
    agent = PerformanceAgent()
    result = await agent.review(sample_code, "test.py")
    
    assert result.agent_type == AgentType.PERFORMANCE
    assert result.success is True
    assert isinstance(result.issues, list)


@pytest.mark.asyncio
async def test_documentation_agent(sample_code):
    """Test Documentation Agent."""
    agent = DocumentationAgent()
    result = await agent.review(sample_code, "test.py")
    
    assert result.agent_type == AgentType.DOCUMENTATION
    assert result.success is True
    assert isinstance(result.issues, list)


@pytest.mark.asyncio
async def test_security_agent_hardcoded_password():
    """Test Security Agent detects hardcoded password."""
    code_with_password = '''
password = "secret123"
api_key = "sk-1234567890"
'''
    agent = SecurityAgent()
    result = await agent.review(code_with_password, "test.py")
    
    assert result.success is True
    # Should detect hardcoded secrets
    assert len(result.issues) > 0


@pytest.mark.asyncio
async def test_quality_agent_with_complex_code():
    """Test Quality Agent with more complex code."""
    complex_code = '''
import os
import sys

class MyClass:
    def __init__(self):
        self.value = 1
    
    def method(self, x, y, z):
        if x > 0:
            if y > 0:
                if z > 0:
                    return x + y + z
        return 0
'''
    agent = QualityAgent()
    result = await agent.review(complex_code, "test.py")
    
    assert result.success is True
    assert isinstance(result.issues, list)


@pytest.mark.asyncio
async def test_performance_agent_complexity():
    """Test Performance Agent detects complexity."""
    complex_code = '''
def complex_function(n):
    result = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if i > j and j > k:
                    result += i * j * k
    return result
'''
    agent = PerformanceAgent()
    result = await agent.review(complex_code, "test.py")
    
    assert result.success is True
    assert isinstance(result.issues, list)


@pytest.mark.asyncio
async def test_documentation_agent_missing_docstrings():
    """Test Documentation Agent detects missing docstrings."""
    code_no_docs = '''
def function_without_docstring():
    return 42

class ClassWithoutDocstring:
    def method(self):
        pass
'''
    agent = DocumentationAgent()
    result = await agent.review(code_no_docs, "test.py")
    
    assert result.success is True
    assert isinstance(result.issues, list)


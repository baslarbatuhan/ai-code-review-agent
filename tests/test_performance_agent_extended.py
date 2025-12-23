"""Extended tests for Performance Agent."""
import pytest
from src.agents.performance_agent import PerformanceAgent
from src.core.schemas import AgentType, Severity
from unittest.mock import patch


@pytest.mark.asyncio
async def test_performance_agent_high_complexity():
    """Test Performance Agent detects very high complexity."""
    agent = PerformanceAgent()
    
    with patch('src.agents.performance_agent.run_radon') as mock_radon:
        mock_radon.return_value = {
            "success": True,
            "complexity": {
                "test.py": [
                    {
                        "name": "very_complex_function",
                        "complexity": 20,
                        "lineno": 1
                    }
                ]
            }
        }
        result = await agent.analyze("def very_complex_function(): pass", "test.py")
        
        assert len(result) > 0
        assert any(issue.issue_type == "high_complexity" for issue in result)
        assert any(issue.severity == Severity.HIGH for issue in result)


@pytest.mark.asyncio
async def test_performance_agent_nested_loops():
    """Test Performance Agent detects nested loops."""
    agent = PerformanceAgent()
    
    code_with_nested_loops = '''
for i in range(10):
    for j in range(10):
        for k in range(10):
            result = i + j + k
            return result
'''
    result = await agent.analyze(code_with_nested_loops, "test.py")
    
    assert any(issue.issue_type == "nested_loops" for issue in result)


@pytest.mark.asyncio
async def test_performance_agent_string_concatenation_in_loop():
    """Test Performance Agent detects string concatenation in loop."""
    agent = PerformanceAgent()
    
    code_with_string_concat = '''
result = ""
for i in range(10):
    result += str(i)
'''
    result = await agent.analyze(code_with_string_concat, "test.py")
    
    assert any(issue.issue_type == "inefficient_string_concat" for issue in result)


@pytest.mark.asyncio
async def test_performance_agent_list_comprehension_opportunity():
    """Test Performance Agent detects list comprehension opportunities."""
    agent = PerformanceAgent()
    
    code_with_append = '''
result = []
for i in range(10):
    result.append(i * 2)
'''
    result = await agent.analyze(code_with_append, "test.py")
    
    assert any(issue.issue_type == "list_comprehension_opportunity" for issue in result)


@pytest.mark.asyncio
async def test_performance_agent_inefficient_operation_keys_sort():
    """Test Performance Agent detects inefficient dict.keys().sort()."""
    agent = PerformanceAgent()
    
    code_inefficient = '''
d = {"a": 1, "b": 2}
keys = d.keys().sort()
'''
    result = await agent.analyze(code_inefficient, "test.py")
    
    assert any(issue.issue_type == "inefficient_operation" for issue in result)


@pytest.mark.asyncio
async def test_performance_agent_inefficient_operation_in_keys():
    """Test Performance Agent detects 'if key in dict.keys()' pattern."""
    agent = PerformanceAgent()
    
    code_inefficient = '''
d = {"a": 1, "b": 2}
if "a" in d.keys():
    pass
'''
    result = await agent.analyze(code_inefficient, "test.py")
    
    assert any(issue.issue_type == "inefficient_operation" for issue in result)


"""Extended tests for Documentation Agent."""
import pytest
from src.agents.documentation_agent import DocumentationAgent
from src.core.schemas import AgentType, Severity


@pytest.mark.asyncio
async def test_documentation_agent_syntax_error():
    """Test Documentation Agent handles syntax errors."""
    agent = DocumentationAgent()
    code_with_syntax_error = '''
def invalid_syntax(
    return 42
'''
    result = await agent.analyze(code_with_syntax_error, "test.py")
    
    assert len(result) > 0
    assert any(issue.issue_type == "syntax_error" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_module_docstring_missing():
    """Test Documentation Agent detects missing module docstring."""
    agent = DocumentationAgent()
    code_no_module_doc = '''
import os
def test():
    pass
'''
    result = await agent.analyze(code_no_module_doc, "test.py")
    
    assert any(issue.issue_type == "missing_module_docstring" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_module_docstring_present():
    """Test Documentation Agent when module docstring is present."""
    agent = DocumentationAgent()
    code_with_module_doc = '''
"""Module docstring."""
import os
def test():
    pass
'''
    result = await agent.analyze(code_with_module_doc, "test.py")
    
    # Should not report missing module docstring
    assert not any(issue.issue_type == "missing_module_docstring" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_function_docstring_missing():
    """Test Documentation Agent detects missing function docstring."""
    agent = DocumentationAgent()
    code_no_func_doc = '''
def test_function():
    return 42
'''
    result = await agent.analyze(code_no_func_doc, "test.py")
    
    assert any(issue.issue_type == "missing_function_docstring" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_function_docstring_short():
    """Test Documentation Agent detects very short docstring."""
    agent = DocumentationAgent()
    code_short_doc = '''
def test_function():
    """Short."""
    return 42
'''
    result = await agent.analyze(code_short_doc, "test.py")
    
    assert any(issue.issue_type == "poor_docstring_quality" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_function_missing_parameter_docs():
    """Test Documentation Agent detects missing parameter documentation."""
    agent = DocumentationAgent()
    code_no_param_docs = '''
def test_function(x, y):
    """This function does something."""
    return x + y
'''
    result = await agent.analyze(code_no_param_docs, "test.py")
    
    assert any(issue.issue_type == "missing_parameter_docs" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_function_with_parameter_docs():
    """Test Documentation Agent when parameters are documented."""
    agent = DocumentationAgent()
    code_with_param_docs = '''
def test_function(x, y):
    """This function does something.
    
    Args:
        x: First parameter
        y: Second parameter
    """
    return x + y
'''
    result = await agent.analyze(code_with_param_docs, "test.py")
    
    # Should not report missing parameter docs
    assert not any(issue.issue_type == "missing_parameter_docs" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_private_function_skipped():
    """Test Documentation Agent skips private functions."""
    agent = DocumentationAgent()
    code_private_func = '''
def _private_function():
    return 42
'''
    result = await agent.analyze(code_private_func, "test.py")
    
    # Should not report missing docstring for private functions
    assert not any(issue.issue_type == "missing_function_docstring" and "_private_function" in issue.message for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_class_docstring_missing():
    """Test Documentation Agent detects missing class docstring."""
    agent = DocumentationAgent()
    code_no_class_doc = '''
class MyClass:
    def method(self):
        pass
'''
    result = await agent.analyze(code_no_class_doc, "test.py")
    
    assert any(issue.issue_type == "missing_class_docstring" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_class_docstring_present():
    """Test Documentation Agent when class docstring is present."""
    agent = DocumentationAgent()
    code_with_class_doc = '''
class MyClass:
    """Class docstring."""
    def method(self):
        pass
'''
    result = await agent.analyze(code_with_class_doc, "test.py")
    
    # Should not report missing class docstring
    assert not any(issue.issue_type == "missing_class_docstring" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_private_class_skipped():
    """Test Documentation Agent skips private classes."""
    agent = DocumentationAgent()
    code_private_class = '''
class _PrivateClass:
    def method(self):
        pass
'''
    result = await agent.analyze(code_private_class, "test.py")
    
    # Should not report missing docstring for private classes
    assert not any(issue.issue_type == "missing_class_docstring" and "_PrivateClass" in issue.message for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_complex_code_no_comments():
    """Test Documentation Agent detects complex code without comments."""
    agent = DocumentationAgent()
    complex_code = '''
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                if x > y:
                    if y > z:
                        return x + y + z
    return 0
'''
    result = await agent.analyze(complex_code, "test.py")
    
    assert any(issue.issue_type == "complex_code_needs_comments" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_complex_code_with_comments():
    """Test Documentation Agent when complex code has comments."""
    agent = DocumentationAgent()
    complex_code_with_comments = '''
def complex_function(x, y, z):
    # Check if all values are positive
    if x > 0:
        # Check y
        if y > 0:
            # Check z
            if z > 0:
                if x > y:
                    if y > z:
                        return x + y + z
    return 0
'''
    result = await agent.analyze(complex_code_with_comments, "test.py")
    
    # Should not report missing comments if comments are present
    assert not any(issue.issue_type == "complex_code_needs_comments" for issue in result)


@pytest.mark.asyncio
async def test_documentation_agent_simple_code_no_comments_needed():
    """Test Documentation Agent doesn't flag simple code."""
    agent = DocumentationAgent()
    simple_code = '''
def simple_function(x):
    return x * 2
'''
    result = await agent.analyze(simple_code, "test.py")
    
    # Should not report complex code issues for simple functions
    assert not any(issue.issue_type == "complex_code_needs_comments" for issue in result)


def test_documentation_agent_calculate_complexity():
    """Test complexity calculation."""
    agent = DocumentationAgent()
    
    # Simple function
    import ast
    simple_code = ast.parse("def test(): return 1")
    simple_func = simple_code.body[0]
    complexity = agent._calculate_complexity(simple_func)
    assert complexity == 1  # Base complexity
    
    # Function with if
    if_code = ast.parse("def test(x):\n    if x > 0:\n        return 1")
    if_func = if_code.body[0]
    complexity = agent._calculate_complexity(if_func)
    assert complexity > 1


@pytest.mark.asyncio
async def test_documentation_agent_code_with_comments_only():
    """Test Documentation Agent with code that has only comments."""
    agent = DocumentationAgent()
    code_with_comments = '''
# This is a comment
# Another comment
x = 1
'''
    result = await agent.analyze(code_with_comments, "test.py")
    
    # Should still check for module docstring
    assert isinstance(result, list)


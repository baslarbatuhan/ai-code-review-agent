"""Extended tests for Security Agent."""
import pytest
from src.agents.security_agent import SecurityAgent
from src.core.schemas import AgentType, Severity
from unittest.mock import patch


@pytest.mark.asyncio
async def test_security_agent_map_bandit_severity_unknown():
    """Test Security Agent maps unknown bandit severity."""
    agent = SecurityAgent()
    
    severity = agent._map_bandit_severity("UNKNOWN")
    assert severity == Severity.LOW


@pytest.mark.asyncio
async def test_security_agent_generate_suggestion_unknown():
    """Test Security Agent generates suggestion for unknown test ID."""
    agent = SecurityAgent()
    
    item = {
        "test_id": "B999",
        "issue_text": "Some security issue"
    }
    suggestion = agent._generate_security_suggestion(item)
    
    assert "Some security issue" in suggestion or "Security concern" in suggestion


@pytest.mark.asyncio
async def test_security_agent_sql_injection_f_string():
    """Test Security Agent detects SQL injection with f-string."""
    agent = SecurityAgent()
    
    code_sql_fstring = '''
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
'''
    result = await agent.analyze(code_sql_fstring, "test.py")
    
    assert any(issue.issue_type == "sql_injection" for issue in result)
    assert any("f-string" in issue.message.lower() for issue in result)


@pytest.mark.asyncio
async def test_security_agent_insecure_random_with_keyword():
    """Test Security Agent detects insecure random with security keywords."""
    agent = SecurityAgent()
    
    code_insecure_random = '''
import random
password = "".join([random.choice("abcdef") for _ in range(10)])
'''
    result = await agent.analyze(code_insecure_random, "test.py")
    
    assert any(issue.issue_type == "insecure_random" for issue in result)


@pytest.mark.asyncio
async def test_security_agent_insecure_random_with_secrets_module():
    """Test Security Agent doesn't flag when secrets module is used."""
    agent = SecurityAgent()
    
    code_with_secrets = '''
import random
import secrets
password = "".join([secrets.choice("abcdef") for _ in range(10)])
'''
    result = await agent.analyze(code_with_secrets, "test.py")
    
    # Should not flag if secrets module is used
    assert not any(issue.issue_type == "insecure_random" for issue in result)


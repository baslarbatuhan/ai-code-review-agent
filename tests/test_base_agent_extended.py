"""Extended tests for Base Agent."""
import pytest
from unittest.mock import Mock, patch
from src.agents.base_agent import BaseAgent
from src.core.schemas import AgentType, Severity, Issue
from src.agents.quality_agent import QualityAgent


@pytest.mark.asyncio
async def test_base_agent_review_success():
    """Test base agent review with successful analysis."""
    agent = QualityAgent()  # Use concrete implementation
    
    result = await agent.review("def test(): pass", "test.py")
    
    assert result.agent_type == AgentType.QUALITY
    assert result.success is True
    assert isinstance(result.issues, list)
    assert result.error_message is None
    assert result.execution_time >= 0
    assert "agent_type" in result.metadata


@pytest.mark.asyncio
async def test_base_agent_review_with_error():
    """Test base agent review when analysis raises exception."""
    agent = QualityAgent()
    
    # Mock analyze to raise exception
    with patch.object(agent, 'analyze', side_effect=Exception("Test error")):
        result = await agent.review("def test(): pass", "test.py")
        
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.issues == []
        assert result.execution_time >= 0


@pytest.mark.asyncio
async def test_base_agent_create_issue():
    """Test base agent create issue method."""
    agent = QualityAgent()
    
    issue = agent._create_issue(
        severity=Severity.HIGH,
        issue_type="test_issue",
        message="Test message",
        line_number=10,
        suggestion="Test suggestion",
        metadata={"key": "value"}
    )
    
    assert issue.severity == Severity.HIGH
    assert issue.issue_type == "test_issue"
    assert issue.message == "Test message"
    assert issue.line_number == 10
    assert issue.suggestion == "Test suggestion"
    assert issue.metadata == {"key": "value"}


@pytest.mark.asyncio
async def test_base_agent_create_issue_minimal():
    """Test base agent create issue with minimal parameters."""
    agent = QualityAgent()
    
    issue = agent._create_issue(
        severity=Severity.LOW,
        issue_type="test_issue",
        message="Test message"
    )
    
    assert issue.severity == Severity.LOW
    assert issue.issue_type == "test_issue"
    assert issue.message == "Test message"
    assert issue.line_number is None
    assert issue.suggestion is None
    assert issue.metadata == {}


@pytest.mark.asyncio
async def test_base_agent_get_metadata():
    """Test base agent get metadata."""
    agent = QualityAgent()
    
    metadata = agent._get_metadata()
    
    assert "agent_type" in metadata
    assert "version" in metadata
    assert metadata["agent_type"] == AgentType.QUALITY.value


@pytest.mark.asyncio
async def test_base_agent_logger():
    """Test base agent logger is set correctly."""
    agent = QualityAgent()
    
    assert agent.logger is not None
    assert agent.agent_type == AgentType.QUALITY


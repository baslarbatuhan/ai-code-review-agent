"""Tests for orchestrator."""
import pytest
from src.core.orchestrator import AgentOrchestrator
from src.core.schemas import AgentType


@pytest.fixture
def sample_code():
    """Sample Python code for testing."""
    return '''
def calculate_sum(a, b):
    return a + b
'''


@pytest.mark.asyncio
async def test_orchestrator_all_agents(sample_code):
    """Test orchestrator with all agents."""
    orchestrator = AgentOrchestrator()
    results = await orchestrator.review_code(sample_code, "test.py")
    
    assert len(results) == 4  # All 4 agents
    assert all(r.success for r in results)


@pytest.mark.asyncio
async def test_orchestrator_specific_agents(sample_code):
    """Test orchestrator with specific agents."""
    orchestrator = AgentOrchestrator()
    results = await orchestrator.review_code(
        sample_code,
        "test.py",
        agent_types=[AgentType.QUALITY, AgentType.SECURITY],
    )
    
    assert len(results) == 2
    assert results[0].agent_type == AgentType.QUALITY
    assert results[1].agent_type == AgentType.SECURITY


@pytest.mark.asyncio
async def test_orchestrator_single_agent(sample_code):
    """Test orchestrator with single agent."""
    orchestrator = AgentOrchestrator()
    results = await orchestrator.review_code(
        sample_code,
        "test.py",
        agent_types=[AgentType.QUALITY],
    )
    
    assert len(results) == 1
    assert results[0].agent_type == AgentType.QUALITY
    assert results[0].success is True


@pytest.mark.asyncio
async def test_orchestrator_empty_code():
    """Test orchestrator with empty code."""
    orchestrator = AgentOrchestrator()
    results = await orchestrator.review_code("", "test.py")
    
    assert len(results) == 4
    assert all(r.success for r in results)


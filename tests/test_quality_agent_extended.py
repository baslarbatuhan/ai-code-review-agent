"""Extended tests for Quality Agent."""
import pytest
from src.agents.quality_agent import QualityAgent
from src.core.schemas import AgentType, Severity
from unittest.mock import patch, Mock


@pytest.mark.asyncio
async def test_quality_agent_map_pylint_severity_error():
    """Test mapping pylint error severity."""
    agent = QualityAgent()
    severity = agent._map_pylint_severity("error")
    assert severity == Severity.HIGH


@pytest.mark.asyncio
async def test_quality_agent_map_pylint_severity_warning():
    """Test mapping pylint warning severity."""
    agent = QualityAgent()
    severity = agent._map_pylint_severity("warning")
    assert severity == Severity.MEDIUM


@pytest.mark.asyncio
async def test_quality_agent_map_pylint_severity_convention():
    """Test mapping pylint convention severity."""
    agent = QualityAgent()
    severity = agent._map_pylint_severity("convention")
    assert severity == Severity.LOW


@pytest.mark.asyncio
async def test_quality_agent_map_pylint_severity_refactor():
    """Test mapping pylint refactor severity."""
    agent = QualityAgent()
    severity = agent._map_pylint_severity("refactor")
    assert severity == Severity.LOW


@pytest.mark.asyncio
async def test_quality_agent_map_pylint_severity_unknown():
    """Test mapping pylint unknown severity."""
    agent = QualityAgent()
    severity = agent._map_pylint_severity("unknown")
    assert severity == Severity.INFO


@pytest.mark.asyncio
async def test_quality_agent_map_pylint_severity_case_insensitive():
    """Test mapping pylint severity is case insensitive."""
    agent = QualityAgent()
    severity_upper = agent._map_pylint_severity("ERROR")
    severity_lower = agent._map_pylint_severity("error")
    assert severity_upper == severity_lower == Severity.HIGH


@pytest.mark.asyncio
async def test_quality_agent_map_flake8_severity_e():
    """Test mapping flake8 E error code."""
    agent = QualityAgent()
    severity = agent._map_flake8_severity("E501")
    assert severity == Severity.HIGH


@pytest.mark.asyncio
async def test_quality_agent_map_flake8_severity_w():
    """Test mapping flake8 W warning code."""
    agent = QualityAgent()
    severity = agent._map_flake8_severity("W503")
    assert severity == Severity.MEDIUM


@pytest.mark.asyncio
async def test_quality_agent_map_flake8_severity_f():
    """Test mapping flake8 F error code."""
    agent = QualityAgent()
    severity = agent._map_flake8_severity("F401")
    assert severity == Severity.HIGH


@pytest.mark.asyncio
async def test_quality_agent_map_flake8_severity_other():
    """Test mapping flake8 other code."""
    agent = QualityAgent()
    severity = agent._map_flake8_severity("C901")
    assert severity == Severity.LOW


@pytest.mark.asyncio
async def test_quality_agent_generate_suggestion_c0103():
    """Test generating suggestion for C0103."""
    agent = QualityAgent()
    item = {"message-id": "C0103", "message": "Invalid name"}
    suggestion = agent._generate_suggestion(item)
    assert "snake_case" in suggestion


@pytest.mark.asyncio
async def test_quality_agent_generate_suggestion_c0111():
    """Test generating suggestion for C0111."""
    agent = QualityAgent()
    item = {"message-id": "C0111", "message": "Missing docstring"}
    suggestion = agent._generate_suggestion(item)
    assert "docstring" in suggestion


@pytest.mark.asyncio
async def test_quality_agent_generate_suggestion_r0903():
    """Test generating suggestion for R0903."""
    agent = QualityAgent()
    item = {"message-id": "R0903", "message": "Too few public methods"}
    suggestion = agent._generate_suggestion(item)
    assert "attributes" in suggestion or "methods" in suggestion


@pytest.mark.asyncio
async def test_quality_agent_generate_suggestion_r0913():
    """Test generating suggestion for R0913."""
    agent = QualityAgent()
    item = {"message-id": "R0913", "message": "Too many arguments"}
    suggestion = agent._generate_suggestion(item)
    assert "parameters" in suggestion or "arguments" in suggestion


@pytest.mark.asyncio
async def test_quality_agent_generate_suggestion_unknown():
    """Test generating suggestion for unknown message ID."""
    agent = QualityAgent()
    item = {"message-id": "UNKNOWN", "message": "Some message"}
    suggestion = agent._generate_suggestion(item)
    assert "Some message" in suggestion or "Review" in suggestion


@pytest.mark.asyncio
async def test_quality_agent_generate_flake8_suggestion_e501():
    """Test generating flake8 suggestion for E501."""
    agent = QualityAgent()
    suggestion = agent._generate_flake8_suggestion("E501")
    assert "long" in suggestion.lower() or "line" in suggestion.lower()


@pytest.mark.asyncio
async def test_quality_agent_generate_flake8_suggestion_e302():
    """Test generating flake8 suggestion for E302."""
    agent = QualityAgent()
    suggestion = agent._generate_flake8_suggestion("E302")
    assert "blank" in suggestion.lower() or "lines" in suggestion.lower()


@pytest.mark.asyncio
async def test_quality_agent_generate_flake8_suggestion_e305():
    """Test generating flake8 suggestion for E305."""
    agent = QualityAgent()
    suggestion = agent._generate_flake8_suggestion("E305")
    assert "blank" in suggestion.lower() or "lines" in suggestion.lower()


@pytest.mark.asyncio
async def test_quality_agent_generate_flake8_suggestion_e401():
    """Test generating flake8 suggestion for E401."""
    agent = QualityAgent()
    suggestion = agent._generate_flake8_suggestion("E401")
    assert "import" in suggestion.lower() or "separate" in suggestion.lower()


@pytest.mark.asyncio
async def test_quality_agent_generate_flake8_suggestion_e402():
    """Test generating flake8 suggestion for E402."""
    agent = QualityAgent()
    suggestion = agent._generate_flake8_suggestion("E402")
    assert "import" in suggestion.lower() or "top" in suggestion.lower()


@pytest.mark.asyncio
async def test_quality_agent_generate_flake8_suggestion_unknown():
    """Test generating flake8 suggestion for unknown code."""
    agent = QualityAgent()
    suggestion = agent._generate_flake8_suggestion("E999")
    assert "PEP 8" in suggestion or "style" in suggestion.lower()


@pytest.mark.asyncio
async def test_quality_agent_with_pylint_results():
    """Test Quality Agent with pylint results."""
    agent = QualityAgent()
    
    with patch('src.agents.quality_agent.run_pylint') as mock_pylint:
        mock_pylint.return_value = {
            "success": True,
            "issues": [
                {
                    "message-id": "C0103",
                    "type": "convention",
                    "message": "Invalid name",
                    "line": 1,
                    "symbol": "invalid-name"
                }
            ]
        }
        with patch('src.agents.quality_agent.run_flake8', return_value={"success": False}):
            with patch('src.agents.quality_agent.run_radon', return_value={"success": False}):
                result = await agent.analyze("def Test(): pass", "test.py")
                
                assert len(result) > 0
                assert any(issue.issue_type == "C0103" for issue in result)


@pytest.mark.asyncio
async def test_quality_agent_with_flake8_results():
    """Test Quality Agent with flake8 results."""
    agent = QualityAgent()
    
    with patch('src.agents.quality_agent.run_pylint', return_value={"success": False}):
        with patch('src.agents.quality_agent.run_flake8') as mock_flake8:
            mock_flake8.return_value = {
                "success": True,
                "issues": [
                    {
                        "code": "E501",
                        "message": "Line too long",
                        "line": 1
                    }
                ]
            }
            with patch('src.agents.quality_agent.run_radon', return_value={"success": False}):
                result = await agent.analyze("x = " + "a" * 100, "test.py")
                
                assert len(result) > 0
                assert any(issue.issue_type == "E501" for issue in result)


@pytest.mark.asyncio
async def test_quality_agent_with_radon_results():
    """Test Quality Agent with radon results."""
    agent = QualityAgent()
    
    with patch('src.agents.quality_agent.run_pylint', return_value={"success": False}):
        with patch('src.agents.quality_agent.run_flake8', return_value={"success": False}):
            with patch('src.agents.quality_agent.run_radon') as mock_radon:
                mock_radon.return_value = {
                    "success": True,
                    "complexity": {
                        "test.py": [
                            {
                                "name": "complex_function",
                                "complexity": 15,
                                "lineno": 1
                            }
                        ]
                    }
                }
                result = await agent.analyze("def complex_function(): pass", "test.py")
                
                assert len(result) > 0
                assert any(issue.issue_type == "high_complexity" for issue in result)


@pytest.mark.asyncio
async def test_quality_agent_with_radon_low_complexity():
    """Test Quality Agent doesn't flag low complexity."""
    agent = QualityAgent()
    
    with patch('src.agents.quality_agent.run_pylint', return_value={"success": False}):
        with patch('src.agents.quality_agent.run_flake8', return_value={"success": False}):
            with patch('src.agents.quality_agent.run_radon') as mock_radon:
                mock_radon.return_value = {
                    "success": True,
                    "complexity": {
                        "test.py": [
                            {
                                "name": "simple_function",
                                "complexity": 3,
                                "lineno": 1
                            }
                        ]
                    }
                }
                result = await agent.analyze("def simple_function(): pass", "test.py")
                
                # Should not flag low complexity
                assert not any(issue.issue_type == "high_complexity" for issue in result)


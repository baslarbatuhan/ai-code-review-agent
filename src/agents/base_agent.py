"""Base agent class for all code review agents."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import logging
from src.core.schemas import AgentResult, AgentType, Issue, Severity

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all code review agents."""

    def __init__(self, agent_type: AgentType):
        """Initialize base agent.

        Args:
            agent_type: Type of the agent
        """
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"{__name__}.{agent_type.value}")

    @abstractmethod
    async def analyze(self, code: str, file_path: str, **kwargs) -> List[Issue]:
        """Analyze code and return issues.

        Args:
            code: Source code to analyze
            file_path: Path to the file being analyzed
            **kwargs: Additional parameters

        Returns:
            List of issues found
        """
        pass

    async def review(self, code: str, file_path: str, **kwargs) -> AgentResult:
        """Review code and return structured result.

        Args:
            code: Source code to review
            file_path: Path to the file being reviewed
            **kwargs: Additional parameters

        Returns:
            AgentResult with issues and metadata
        """
        start_time = time.time()
        issues = []
        error_message = None
        success = True

        try:
            issues = await self.analyze(code, file_path, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in {self.agent_type.value} agent: {str(e)}", exc_info=True)
            error_message = str(e)
            success = False

        execution_time = time.time() - start_time

        return AgentResult(
            agent_type=self.agent_type,
            success=success,
            execution_time=execution_time,
            issues=issues,
            error_message=error_message,
            metadata=self._get_metadata(),
        )

    def _get_metadata(self) -> Dict[str, Any]:
        """Get agent-specific metadata.

        Returns:
            Dictionary with metadata
        """
        return {
            "agent_type": self.agent_type.value,
            "version": "1.0.0",
        }

    def _create_issue(
        self,
        severity: Severity,
        issue_type: str,
        message: str,
        line_number: Optional[int] = None,
        suggestion: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Issue:
        """Create an issue object.

        Args:
            severity: Issue severity
            issue_type: Type of issue
            message: Issue message
            line_number: Line number where issue occurs
            suggestion: Suggested fix
            metadata: Additional metadata

        Returns:
            Issue object
        """
        return Issue(
            severity=severity,
            issue_type=issue_type,
            message=message,
            line_number=line_number,
            suggestion=suggestion,
            metadata=metadata or {},
        )


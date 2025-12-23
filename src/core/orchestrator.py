"""Agent orchestrator for coordinating multiple agents."""
from typing import List, Optional
import asyncio
import logging
from src.agents import (
    QualityAgent,
    SecurityAgent,
    PerformanceAgent,
    DocumentationAgent,
)
from src.core.schemas import AgentResult, AgentType

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrator for coordinating multiple code review agents."""

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.quality_agent = QualityAgent()
        self.security_agent = SecurityAgent()
        self.performance_agent = PerformanceAgent()
        self.documentation_agent = DocumentationAgent()

        self.agents = {
            AgentType.QUALITY: self.quality_agent,
            AgentType.SECURITY: self.security_agent,
            AgentType.PERFORMANCE: self.performance_agent,
            AgentType.DOCUMENTATION: self.documentation_agent,
        }

    async def review_code(
        self,
        code: str,
        file_path: str,
        agent_types: Optional[List[AgentType]] = None,
        **kwargs,
    ) -> List[AgentResult]:
        """Review code using specified agents (or all if not specified).

        Args:
            code: Source code to review
            file_path: Path to the file
            agent_types: List of agent types to run (None = all)
            **kwargs: Additional parameters

        Returns:
            List of agent results
        """
        if agent_types is None:
            agent_types = list(AgentType)

        # Run agents in parallel
        tasks = []
        for agent_type in agent_types:
            if agent_type in self.agents:
                agent = self.agents[agent_type]
                tasks.append(agent.review(code, file_path, **kwargs))

        # Wait for all agents to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        agent_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_types[i]} failed: {str(result)}", exc_info=result)
                agent_results.append(
                    AgentResult(
                        agent_type=agent_types[i],
                        success=False,
                        execution_time=0.0,
                        issues=[],
                        error_message=str(result),
                    )
                )
            else:
                agent_results.append(result)

        return agent_results

    def get_agent(self, agent_type: AgentType):
        """Get a specific agent by type.

        Args:
            agent_type: Type of agent

        Returns:
            Agent instance
        """
        return self.agents.get(agent_type)


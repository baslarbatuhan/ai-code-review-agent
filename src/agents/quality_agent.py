"""Quality Agent for code style and quality analysis."""
from typing import List
from src.agents.base_agent import BaseAgent
from src.core.schemas import AgentType, Issue, Severity
from src.utils.static_analysis import run_pylint, run_flake8, run_radon
import logging

logger = logging.getLogger(__name__)


class QualityAgent(BaseAgent):
    """Agent responsible for code quality analysis."""

    def __init__(self):
        """Initialize Quality Agent."""
        super().__init__(AgentType.QUALITY)

    async def analyze(self, code: str, file_path: str, **kwargs) -> List[Issue]:
        """Analyze code quality using static analysis tools.

        Args:
            code: Source code to analyze
            file_path: Path to the file
            **kwargs: Additional parameters

        Returns:
            List of quality issues
        """
        issues = []

        # Run pylint
        pylint_results = run_pylint(code, file_path)
        if pylint_results.get("success"):
            for item in pylint_results.get("issues", []):
                severity = self._map_pylint_severity(item.get("type", ""))
                issues.append(
                    self._create_issue(
                        severity=severity,
                        issue_type=item.get("message-id", "pylint"),
                        message=item.get("message", ""),
                        line_number=item.get("line"),
                        suggestion=self._generate_suggestion(item),
                        metadata={"tool": "pylint", "symbol": item.get("symbol", "")},
                    )
                )

        # Run flake8
        flake8_results = run_flake8(code, file_path)
        if flake8_results.get("success"):
            for item in flake8_results.get("issues", []):
                severity = self._map_flake8_severity(item.get("code", ""))
                issues.append(
                    self._create_issue(
                        severity=severity,
                        issue_type=item.get("code", "flake8"),
                        message=item.get("message", ""),
                        line_number=item.get("line"),
                        suggestion=self._generate_flake8_suggestion(item.get("code", "")),
                        metadata={"tool": "flake8"},
                    )
                )

        # Run radon for complexity
        radon_results = run_radon(code, file_path)
        if radon_results.get("success"):
            complexity_data = radon_results.get("complexity", {})
            for file_path_key, functions in complexity_data.items():
                if isinstance(functions, list):
                    for func in functions:
                        complexity = func.get("complexity", 0)
                        if complexity > 10:  # High complexity threshold
                            issues.append(
                                self._create_issue(
                                    severity=Severity.MEDIUM,
                                    issue_type="high_complexity",
                                    message=f"Function '{func.get('name', 'unknown')}' has high complexity ({complexity})",
                                    line_number=func.get("lineno"),
                                    suggestion="Consider refactoring this function into smaller, more manageable pieces.",
                                    metadata={
                                        "tool": "radon",
                                        "complexity": complexity,
                                        "function": func.get("name"),
                                    },
                                )
                            )

        return issues

    def _map_pylint_severity(self, pylint_type: str) -> Severity:
        """Map pylint severity to our severity enum.

        Args:
            pylint_type: Pylint message type (error, warning, convention, refactor)

        Returns:
            Severity level
        """
        mapping = {
            "error": Severity.HIGH,
            "warning": Severity.MEDIUM,
            "convention": Severity.LOW,
            "refactor": Severity.LOW,
        }
        return mapping.get(pylint_type.lower(), Severity.INFO)

    def _map_flake8_severity(self, code: str) -> Severity:
        """Map flake8 error code to severity.

        Args:
            code: Flake8 error code (E, W, F, etc.)

        Returns:
            Severity level
        """
        if code.startswith("E"):  # Error
            return Severity.HIGH
        elif code.startswith("W"):  # Warning
            return Severity.MEDIUM
        elif code.startswith("F"):  # PyFlakes error
            return Severity.HIGH
        else:
            return Severity.LOW

    def _generate_suggestion(self, pylint_item: dict) -> str:
        """Generate suggestion from pylint result.

        Args:
            pylint_item: Pylint result item

        Returns:
            Suggestion string
        """
        message_id = pylint_item.get("message-id", "")
        message = pylint_item.get("message", "")

        # Common suggestions based on message ID
        suggestions = {
            "C0103": "Use snake_case for variable names",
            "C0111": "Add docstring to function/class",
            "R0903": "Consider reducing the number of attributes",
            "R0913": "Reduce the number of parameters",
        }

        if message_id in suggestions:
            return suggestions[message_id]

        return f"Review: {message}"

    def _generate_flake8_suggestion(self, code: str) -> str:
        """Generate suggestion from flake8 error code.

        Args:
            code: Flake8 error code

        Returns:
            Suggestion string
        """
        suggestions = {
            "E501": "Line too long. Consider breaking it into multiple lines.",
            "E302": "Expected 2 blank lines before function/class definition.",
            "E305": "Expected 2 blank lines after class/function definition.",
            "E401": "Multiple imports on one line. Use separate import statements.",
            "E402": "Module level import not at top of file.",
        }

        return suggestions.get(code, "Review PEP 8 style guide for this issue.")


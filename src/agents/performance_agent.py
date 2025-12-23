"""Performance Agent for performance bottleneck detection."""
from typing import List
from src.agents.base_agent import BaseAgent
from src.core.schemas import AgentType, Issue, Severity
from src.utils.static_analysis import run_radon
import logging
import re
import ast

logger = logging.getLogger(__name__)


class PerformanceAgent(BaseAgent):
    """Agent responsible for performance analysis."""

    def __init__(self):
        """Initialize Performance Agent."""
        super().__init__(AgentType.PERFORMANCE)

    async def analyze(self, code: str, file_path: str, **kwargs) -> List[Issue]:
        """Analyze code for performance issues.

        Args:
            code: Source code to analyze
            file_path: Path to the file
            **kwargs: Additional parameters

        Returns:
            List of performance issues
        """
        issues = []

        # Run radon for complexity analysis
        radon_results = run_radon(code, file_path)
        if radon_results.get("success"):
            complexity_data = radon_results.get("complexity", {})
            for file_path_key, functions in complexity_data.items():
                if isinstance(functions, list):
                    for func in functions:
                        complexity = func.get("complexity", 0)
                        if complexity > 15:  # Very high complexity
                            issues.append(
                                self._create_issue(
                                    severity=Severity.HIGH,
                                    issue_type="high_complexity",
                                    message=f"Function '{func.get('name', 'unknown')}' has very high complexity ({complexity}) which may impact performance",
                                    line_number=func.get("lineno"),
                                    suggestion="Refactor into smaller functions. Consider using caching or optimization techniques.",
                                    metadata={
                                        "tool": "radon",
                                        "complexity": complexity,
                                        "function": func.get("name"),
                                    },
                                )
                            )

        # Check for common performance anti-patterns
        issues.extend(self._check_nested_loops(code, file_path))
        issues.extend(self._check_string_concatenation(code, file_path))
        issues.extend(self._check_list_comprehension_opportunities(code, file_path))
        issues.extend(self._check_inefficient_operations(code, file_path))

        return issues

    def _check_nested_loops(self, code: str, file_path: str) -> List[Issue]:
        """Check for deeply nested loops that may impact performance.

        Args:
            code: Source code
            file_path: File path

        Returns:
            List of performance issues
        """
        issues = []
        lines = code.split("\n")
        loop_depth = 0
        max_depth = 0
        start_line = 0

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(("for ", "while ")):
                loop_depth += 1
                if loop_depth == 1:
                    start_line = line_num
                max_depth = max(max_depth, loop_depth)
            elif stripped.startswith(("if ", "elif ", "else:")):
                # Nested conditions also add complexity
                pass
            elif stripped and not stripped.startswith("#"):
                # Check if we're closing a loop
                if loop_depth > 0 and (stripped.startswith("return") or stripped.startswith("break")):
                    if max_depth >= 3:
                        issues.append(
                            self._create_issue(
                                severity=Severity.MEDIUM,
                                issue_type="nested_loops",
                                message=f"Deeply nested loops detected (depth: {max_depth})",
                                line_number=start_line,
                                suggestion="Consider optimizing nested loops. Use itertools.product() or vectorized operations if possible.",
                                metadata={"depth": max_depth},
                            )
                        )
                    loop_depth = 0
                    max_depth = 0

        return issues

    def _check_string_concatenation(self, code: str, file_path: str) -> List[Issue]:
        """Check for inefficient string concatenation in loops.

        Args:
            code: Source code
            file_path: File path

        Returns:
            List of performance issues
        """
        issues = []
        lines = code.split("\n")

        # Pattern for string concatenation in loops
        pattern = r'(\w+)\s*\+=\s*["\']'

        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                # Check if it's in a loop context (simplified check)
                if line_num > 1 and any(
                    keyword in lines[line_num - 2].lower() for keyword in ["for ", "while "]
                ):
                    issues.append(
                        self._create_issue(
                            severity=Severity.MEDIUM,
                            issue_type="inefficient_string_concat",
                            message="String concatenation in loop detected",
                            line_number=line_num,
                            suggestion="Use list.append() and ''.join() for better performance in loops.",
                            metadata={"line": line.strip()},
                        )
                    )

        return issues

    def _check_list_comprehension_opportunities(self, code: str, file_path: str) -> List[Issue]:
        """Check for opportunities to use list comprehensions.

        Args:
            code: Source code
            file_path: File path

        Returns:
            List of performance issues
        """
        issues = []
        lines = code.split("\n")

        # Simple pattern: list.append() in a for loop
        for i, line in enumerate(lines):
            if "append(" in line and i > 0:
                prev_line = lines[i - 1].strip()
                if prev_line.startswith("for "):
                    issues.append(
                        self._create_issue(
                            severity=Severity.LOW,
                            issue_type="list_comprehension_opportunity",
                            message="Consider using list comprehension instead of loop with append",
                            line_number=i + 1,
                            suggestion="List comprehensions are generally faster and more Pythonic.",
                            metadata={"line": line.strip()},
                        )
                    )

        return issues

    def _check_inefficient_operations(self, code: str, file_path: str) -> List[Issue]:
        """Check for other inefficient operations.

        Args:
            code: Source code
            file_path: File path

        Returns:
            List of performance issues
        """
        issues = []
        lines = code.split("\n")

        # Check for inefficient patterns
        patterns = [
            (r'\.keys\(\)\.sort\(\)', "Use sorted(dict.keys()) instead of .keys().sort()"),
            (r'if\s+\w+\s+in\s+dict\.keys\(\)', "Use 'if key in dict' instead of 'if key in dict.keys()'"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, suggestion in patterns:
                if re.search(pattern, line):
                    issues.append(
                        self._create_issue(
                            severity=Severity.LOW,
                            issue_type="inefficient_operation",
                            message="Inefficient operation detected",
                            line_number=line_num,
                            suggestion=suggestion,
                            metadata={"line": line.strip()},
                        )
                    )

        return issues


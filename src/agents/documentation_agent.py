"""Documentation Agent for documentation quality analysis."""
from typing import List
from src.agents.base_agent import BaseAgent
from src.core.schemas import AgentType, Issue, Severity
import logging
import ast
import re

logger = logging.getLogger(__name__)


class DocumentationAgent(BaseAgent):
    """Agent responsible for documentation analysis."""

    def __init__(self):
        """Initialize Documentation Agent."""
        super().__init__(AgentType.DOCUMENTATION)

    async def analyze(self, code: str, file_path: str, **kwargs) -> List[Issue]:
        """Analyze code documentation quality.

        Args:
            code: Source code to analyze
            file_path: Path to the file
            **kwargs: Additional parameters

        Returns:
            List of documentation issues
        """
        issues = []

        try:
            # Parse AST to analyze code structure
            tree = ast.parse(code)
            issues.extend(self._check_module_docstring(code, file_path))
            issues.extend(self._check_function_docstrings(tree, code))
            issues.extend(self._check_class_docstrings(tree, code))
            issues.extend(self._check_complex_code_comments(tree, code))
        except SyntaxError:
            # If code has syntax errors, skip AST analysis
            logger.warning(f"Syntax error in {file_path}, skipping AST analysis")
            issues.append(
                self._create_issue(
                    severity=Severity.HIGH,
                    issue_type="syntax_error",
                    message="Code has syntax errors, cannot analyze documentation",
                    line_number=None,
                    suggestion="Fix syntax errors first",
                )
            )

        return issues

    def _check_module_docstring(self, code: str, file_path: str) -> List[Issue]:
        """Check if module has a docstring.

        Args:
            code: Source code
            file_path: File path

        Returns:
            List of documentation issues
        """
        issues = []
        lines = code.split("\n")

        # Check first non-empty, non-comment line
        first_line_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                first_line_idx = i
                break

        # Check if first line is a docstring
        if first_line_idx < len(lines):
            first_line = lines[first_line_idx].strip()
            if not (first_line.startswith('"""') or first_line.startswith("'''")):
                issues.append(
                    self._create_issue(
                        severity=Severity.LOW,
                        issue_type="missing_module_docstring",
                        message="Module is missing a docstring",
                        line_number=1,
                        suggestion="Add a module-level docstring describing the module's purpose.",
                    )
                )

        return issues

    def _check_function_docstrings(self, tree: ast.AST, code: str) -> List[Issue]:
        """Check function docstrings.

        Args:
            tree: AST tree
            code: Source code

        Returns:
            List of documentation issues
        """
        issues = []
        lines = code.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions (starting with _)
                if node.name.startswith("_"):
                    continue

                # Check if function has docstring
                if not ast.get_docstring(node):
                    line_num = node.lineno
                    issues.append(
                        self._create_issue(
                            severity=Severity.MEDIUM,
                            issue_type="missing_function_docstring",
                            message=f"Function '{node.name}' is missing a docstring",
                            line_number=line_num,
                            suggestion=f"Add a docstring to function '{node.name}' describing its purpose, parameters, and return value.",
                            metadata={"function": node.name},
                        )
                    )
                else:
                    # Check docstring quality
                    docstring = ast.get_docstring(node)
                    if len(docstring) < 20:  # Very short docstring
                        line_num = node.lineno
                        issues.append(
                            self._create_issue(
                                severity=Severity.LOW,
                                issue_type="poor_docstring_quality",
                                message=f"Function '{node.name}' has a very brief docstring",
                                line_number=line_num,
                                suggestion="Expand the docstring to include parameter descriptions and return value information.",
                                metadata={"function": node.name},
                            )
                        )

                    # Check for parameter documentation
                    if node.args.args:
                        if not any("param" in docstring.lower() or "arg" in docstring.lower() for word in docstring.split()):
                            line_num = node.lineno
                            issues.append(
                                self._create_issue(
                                    severity=Severity.LOW,
                                    issue_type="missing_parameter_docs",
                                    message=f"Function '{node.name}' docstring doesn't document parameters",
                                    line_number=line_num,
                                    suggestion="Document function parameters in the docstring.",
                                    metadata={"function": node.name},
                                )
                            )

        return issues

    def _check_class_docstrings(self, tree: ast.AST, code: str) -> List[Issue]:
        """Check class docstrings.

        Args:
            tree: AST tree
            code: Source code

        Returns:
            List of documentation issues
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Skip private classes (starting with _)
                if node.name.startswith("_"):
                    continue

                # Check if class has docstring
                if not ast.get_docstring(node):
                    line_num = node.lineno
                    issues.append(
                        self._create_issue(
                            severity=Severity.MEDIUM,
                            issue_type="missing_class_docstring",
                            message=f"Class '{node.name}' is missing a docstring",
                            line_number=line_num,
                            suggestion=f"Add a docstring to class '{node.name}' describing its purpose and usage.",
                            metadata={"class": node.name},
                        )
                    )

        return issues

    def _check_complex_code_comments(self, tree: ast.AST, code: str) -> List[Issue]:
        """Check for complex code that might need comments.

        Args:
            tree: AST tree
            code: Source code

        Returns:
            List of documentation issues
        """
        issues = []
        lines = code.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function complexity
                complexity = self._calculate_complexity(node)
                if complexity > 5:  # High complexity
                    # Check if there are comments in the function
                    function_lines = lines[node.lineno - 1 : node.end_lineno]
                    has_comments = any(line.strip().startswith("#") for line in function_lines)

                    if not has_comments:
                        issues.append(
                            self._create_issue(
                                severity=Severity.LOW,
                                issue_type="complex_code_needs_comments",
                                message=f"Complex function '{node.name}' lacks inline comments",
                                line_number=node.lineno,
                                suggestion="Add inline comments to explain complex logic.",
                                metadata={"function": node.name, "complexity": complexity},
                            )
                        )

        return issues

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function.

        Args:
            node: AST node (function)

        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


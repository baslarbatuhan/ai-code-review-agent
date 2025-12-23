"""Security Agent for security vulnerability detection."""
from typing import List
from src.agents.base_agent import BaseAgent
from src.core.schemas import AgentType, Issue, Severity
from src.utils.static_analysis import run_bandit
import logging
import re

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """Agent responsible for security vulnerability detection."""

    def __init__(self):
        """Initialize Security Agent."""
        super().__init__(AgentType.SECURITY)

    async def analyze(self, code: str, file_path: str, **kwargs) -> List[Issue]:
        """Analyze code for security vulnerabilities.

        Args:
            code: Source code to analyze
            file_path: Path to the file
            **kwargs: Additional parameters

        Returns:
            List of security issues
        """
        issues = []

        # Run bandit security scanner
        bandit_results = run_bandit(code, file_path)
        if bandit_results.get("success"):
            for item in bandit_results.get("issues", []):
                severity = self._map_bandit_severity(item.get("issue_severity", "LOW"))
                issues.append(
                    self._create_issue(
                        severity=severity,
                        issue_type=item.get("test_id", "security"),
                        message=item.get("issue_text", ""),
                        line_number=item.get("line_number"),
                        suggestion=self._generate_security_suggestion(item),
                        metadata={
                            "tool": "bandit",
                            "confidence": item.get("issue_confidence", "MEDIUM"),
                            "cwe": item.get("issue_cwe", {}),
                        },
                    )
                )

        # Additional custom security checks
        issues.extend(self._check_hardcoded_secrets(code, file_path))
        issues.extend(self._check_sql_injection(code, file_path))
        issues.extend(self._check_insecure_random(code, file_path))

        return issues

    def _map_bandit_severity(self, bandit_severity: str) -> Severity:
        """Map bandit severity to our severity enum.

        Args:
            bandit_severity: Bandit severity level

        Returns:
            Severity level
        """
        mapping = {
            "HIGH": Severity.CRITICAL,
            "MEDIUM": Severity.HIGH,
            "LOW": Severity.MEDIUM,
        }
        return mapping.get(bandit_severity.upper(), Severity.LOW)

    def _generate_security_suggestion(self, bandit_item: dict) -> str:
        """Generate security suggestion from bandit result.

        Args:
            bandit_item: Bandit result item

        Returns:
            Suggestion string
        """
        test_id = bandit_item.get("test_id", "")
        issue_text = bandit_item.get("issue_text", "")

        suggestions = {
            "B101": "Use assert statements only for debugging, not for production code.",
            "B104": "Hardcoded bind to all interfaces. Use specific IP address.",
            "B105": "Hardcoded password string. Use environment variables or secure vault.",
            "B106": "Hardcoded password in function call. Use secure credential management.",
            "B107": "Hardcoded password in string. Never hardcode passwords.",
            "B201": "Flask app detected with debug=True. Disable debug mode in production.",
            "B301": "Use of pickle. Only unpickle data from trusted sources.",
            "B506": "Use of shell=True in subprocess. Avoid shell injection vulnerabilities.",
            "B602": "Shell injection via subprocess. Use shell=False or escape arguments.",
        }

        if test_id in suggestions:
            return suggestions[test_id]

        return f"Security concern: {issue_text}. Review security best practices."

    def _check_hardcoded_secrets(self, code: str, file_path: str) -> List[Issue]:
        """Check for hardcoded secrets and credentials.

        Args:
            code: Source code
            file_path: File path

        Returns:
            List of security issues
        """
        issues = []
        lines = code.split("\n")

        # Patterns for common secrets
        secret_patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\']([^"\']+)["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\']([^"\']+)["\']', "Hardcoded secret detected"),
            (r'token\s*=\s*["\']([^"\']+)["\']', "Hardcoded token detected"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, message in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        self._create_issue(
                            severity=Severity.CRITICAL,
                            issue_type="hardcoded_secret",
                            message=message,
                            line_number=line_num,
                            suggestion="Use environment variables or secure credential management system.",
                            metadata={"pattern": pattern, "line": line.strip()},
                        )
                    )

        return issues

    def _check_sql_injection(self, code: str, file_path: str) -> List[Issue]:
        """Check for SQL injection vulnerabilities.

        Args:
            code: Source code
            file_path: File path

        Returns:
            List of security issues
        """
        issues = []
        lines = code.split("\n")

        # Pattern for string formatting in SQL queries
        sql_pattern = r'execute\s*\([^)]*%\s*[%s]'
        sql_f_string = r'execute\s*\([^)]*f["\']'

        for line_num, line in enumerate(lines, 1):
            if re.search(sql_pattern, line, re.IGNORECASE):
                issues.append(
                    self._create_issue(
                        severity=Severity.CRITICAL,
                        issue_type="sql_injection",
                        message="Potential SQL injection vulnerability detected",
                        line_number=line_num,
                        suggestion="Use parameterized queries or ORM methods instead of string formatting.",
                        metadata={"line": line.strip()},
                    )
                )
            elif re.search(sql_f_string, line, re.IGNORECASE):
                issues.append(
                    self._create_issue(
                        severity=Severity.CRITICAL,
                        issue_type="sql_injection",
                        message="Potential SQL injection vulnerability with f-string",
                        line_number=line_num,
                        suggestion="Use parameterized queries or ORM methods instead of f-strings.",
                        metadata={"line": line.strip()},
                    )
                )

        return issues

    def _check_insecure_random(self, code: str, file_path: str) -> List[Issue]:
        """Check for insecure random number generation.

        Args:
            code: Source code
            file_path: File path

        Returns:
            List of security issues
        """
        issues = []
        lines = code.split("\n")

        # Check for use of random module for security purposes
        random_pattern = r'random\.(randint|choice|random)'
        uses_secrets = "secrets" in code.lower()

        for line_num, line in enumerate(lines, 1):
            if re.search(random_pattern, line) and not uses_secrets:
                # Check if it's used for security-sensitive purposes
                if any(keyword in line.lower() for keyword in ["password", "token", "key", "secret", "auth"]):
                    issues.append(
                        self._create_issue(
                            severity=Severity.HIGH,
                            issue_type="insecure_random",
                            message="Using random module for security-sensitive operations",
                            line_number=line_num,
                            suggestion="Use secrets module for cryptographically secure random number generation.",
                            metadata={"line": line.strip()},
                        )
                    )

        return issues


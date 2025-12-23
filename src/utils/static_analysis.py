"""Utilities for running static analysis tools."""
import subprocess
import json
import tempfile
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def run_pylint(code: str, file_path: str) -> Dict[str, Any]:
    """Run pylint on code.

    Args:
        code: Source code to analyze
        file_path: Path to the file

    Returns:
        Dictionary with pylint results
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            # Run pylint
            result = subprocess.run(
                ["pylint", "--output-format=json", temp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse JSON output
            if result.stdout:
                issues = json.loads(result.stdout)
                return {"success": True, "issues": issues, "output": result.stderr}
            else:
                return {"success": True, "issues": [], "output": result.stderr}

        finally:
            # Clean up temp file
            os.unlink(temp_path)

    except subprocess.TimeoutExpired:
        logger.warning("pylint timed out")
        return {"success": False, "issues": [], "error": "Timeout"}
    except Exception as e:
        logger.error(f"Error running pylint: {str(e)}")
        return {"success": False, "issues": [], "error": str(e)}


def run_flake8(code: str, file_path: str) -> Dict[str, Any]:
    """Run flake8 on code.

    Args:
        code: Source code to analyze
        file_path: Path to the file

    Returns:
        Dictionary with flake8 results
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            # Run flake8
            result = subprocess.run(
                ["flake8", "--format=json", temp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse output (flake8 doesn't have native JSON, so we parse text)
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        # Format: path:line:col: code message
                        parts = line.split(":", 3)
                        if len(parts) >= 4:
                            issues.append(
                                {
                                    "path": parts[0],
                                    "line": int(parts[1]),
                                    "column": int(parts[2]),
                                    "code": parts[3].split()[0] if parts[3] else "",
                                    "message": parts[3].strip() if len(parts[3]) > 0 else "",
                                }
                            )

            return {"success": True, "issues": issues, "output": result.stderr}

        finally:
            os.unlink(temp_path)

    except subprocess.TimeoutExpired:
        logger.warning("flake8 timed out")
        return {"success": False, "issues": [], "error": "Timeout"}
    except Exception as e:
        logger.error(f"Error running flake8: {str(e)}")
        return {"success": False, "issues": [], "error": str(e)}


def run_bandit(code: str, file_path: str) -> Dict[str, Any]:
    """Run bandit security scanner on code.

    Args:
        code: Source code to analyze
        file_path: Path to the file

    Returns:
        Dictionary with bandit results
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            # Run bandit
            result = subprocess.run(
                ["bandit", "-f", "json", temp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse JSON output
            if result.stdout:
                data = json.loads(result.stdout)
                return {
                    "success": True,
                    "issues": data.get("results", []),
                    "metrics": data.get("metrics", {}),
                }
            else:
                return {"success": True, "issues": [], "metrics": {}}

        finally:
            os.unlink(temp_path)

    except subprocess.TimeoutExpired:
        logger.warning("bandit timed out")
        return {"success": False, "issues": [], "error": "Timeout"}
    except Exception as e:
        logger.error(f"Error running bandit: {str(e)}")
        return {"success": False, "issues": [], "error": str(e)}


def run_radon(code: str, file_path: str) -> Dict[str, Any]:
    """Run radon complexity analyzer on code.

    Args:
        code: Source code to analyze
        file_path: Path to the file

    Returns:
        Dictionary with radon results
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            # Run radon for complexity
            complexity_result = subprocess.run(
                ["radon", "cc", "-j", temp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Run radon for maintainability index
            mi_result = subprocess.run(
                ["radon", "mi", "-j", temp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            complexity_data = {}
            mi_data = {}

            if complexity_result.stdout:
                complexity_data = json.loads(complexity_result.stdout)

            if mi_result.stdout:
                mi_data = json.loads(mi_result.stdout)

            return {
                "success": True,
                "complexity": complexity_data,
                "maintainability": mi_data,
            }

        finally:
            os.unlink(temp_path)

    except subprocess.TimeoutExpired:
        logger.warning("radon timed out")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        logger.error(f"Error running radon: {str(e)}")
        return {"success": False, "error": str(e)}


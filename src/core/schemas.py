"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AgentType(str, Enum):
    """Agent types."""

    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"


class ReviewRequest(BaseModel):
    """Request model for code review."""

    repository_url: str = Field(..., description="GitHub/GitLab repository URL")
    file_path: Optional[str] = Field(None, description="Specific file path to review")
    commit_sha: Optional[str] = Field(None, description="Specific commit SHA")
    pull_request_id: Optional[int] = Field(None, description="Pull request ID")
    scan_entire_repo: Optional[bool] = Field(
        False, description="Scan entire repository for all Python files (ignores file_path if True)"
    )
    agent_types: Optional[List[AgentType]] = Field(
        None, description="Specific agents to run (default: all)"
    )


class Issue(BaseModel):
    """Code review issue."""

    severity: Severity
    issue_type: str
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResult(BaseModel):
    """Result from a single agent."""

    agent_type: AgentType
    success: bool
    execution_time: float
    issues: List[Issue]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ReviewResponse(BaseModel):
    """Response model for code review."""

    review_id: int
    repository_url: str
    file_path: str
    status: str
    results: List[AgentResult]
    total_issues: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class RepositoryInfo(BaseModel):
    """Repository information."""

    name: str
    url: str
    platform: str
    owner: str


"""Database models for the code review system."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.connection import Base


class Repository(Base):
    """Repository model."""

    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False)  # github or gitlab
    owner = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviews = relationship("Review", back_populates="repository")


class Review(Base):
    """Code review model."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    commit_sha = Column(String(40), nullable=True)
    pull_request_id = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="reviews")
    results = relationship("ReviewResult", back_populates="review")


class ReviewResult(Base):
    """Review result from individual agents."""

    __tablename__ = "review_results"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    agent_type = Column(String(50), nullable=False)  # quality, security, performance, documentation
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    issue_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    line_number = Column(Integer, nullable=True)
    suggestion = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)  # Additional data from agents (renamed from metadata - reserved word)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="results")


class AgentMetrics(Base):
    """Agent performance metrics."""

    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(50), nullable=False)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=True)
    execution_time = Column(Float, nullable=False)  # seconds
    issues_found = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    """User feedback on review suggestions."""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    review_result_id = Column(Integer, ForeignKey("review_results.id"), nullable=False)
    feedback_type = Column(String(20), nullable=False)  # accepted, rejected, modified
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


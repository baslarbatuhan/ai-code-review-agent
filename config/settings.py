"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    # Default to SQLite for development (no Docker/PostgreSQL required)
    database_url: str = "sqlite:///./code_review.db"
    redis_url: str = "redis://localhost:6379/0"

    # LLM Configuration
    llm_provider: str = "ollama"  # Options: ollama, openai
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    openai_api_key: Optional[str] = None

    # GitHub/GitLab Configuration
    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    gitlab_url: str = "https://gitlab.com"

    # Application Configuration
    app_name: str = "AI Code Review Agent"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Streamlit Configuration
    streamlit_port: int = 8501

    # Security
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Rate Limiting
    rate_limit_per_minute: int = 60

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


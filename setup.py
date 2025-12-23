"""Setup script for AI Code Review Agent."""
from setuptools import setup, find_packages

setup(
    name="ai-code-review-agent",
    version="1.0.0",
    description="AI-Powered Code Review Agent",
    author="Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9",
        "redis>=5.0.1",
        "pylint>=3.0.2",
        "flake8>=6.1.0",
        "bandit>=1.7.5",
        "radon>=6.0.1",
        "langchain>=0.1.0",
        "PyGithub>=1.59.1",
        "python-gitlab>=4.1.0",
        "streamlit>=1.28.1",
        "pytest>=7.4.3",
    ],
)


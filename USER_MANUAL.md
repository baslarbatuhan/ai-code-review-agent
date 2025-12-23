# 📖 User Manual - AI-Powered Code Review Agent

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Course:** SEN0414 Advanced Programming - Istanbul Kültür University

---

## 📋 Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Installation Guide](#3-installation-guide)
4. [Configuration](#4-configuration)
5. [Getting Started](#5-getting-started)
6. [Using the Web Dashboard](#6-using-the-web-dashboard)
7. [Using the API](#7-using-the-api)
8. [Common Use Cases](#8-common-use-cases)
9. [Troubleshooting](#9-troubleshooting)
10. [Advanced Features](#10-advanced-features)
11. [FAQ](#11-faq)

---

## 1. Introduction

### 1.1 What is AI-Powered Code Review Agent?

The AI-Powered Code Review Agent is an intelligent multi-agent system that automatically reviews Python code for:
- **Code Quality** - Style, best practices, PEP 8 compliance
- **Security** - Vulnerabilities, hardcoded secrets, SQL injection risks
- **Performance** - Complexity, bottlenecks, optimization opportunities
- **Documentation** - Missing docstrings, code comments, documentation quality

### 1.2 Key Features

- ✅ **Multi-Agent Architecture** - Four specialized agents working in parallel
- ✅ **GitHub/GitLab Integration** - Direct repository access
- ✅ **Static Analysis** - Integrates pylint, flake8, bandit, and radon
- ✅ **LLM-Powered Suggestions** - Intelligent recommendations using AI
- ✅ **Web Dashboard** - User-friendly interface for reviews and analytics
- ✅ **REST API** - Programmatic access for CI/CD integration

### 1.3 Who Should Use This?

- **Developers** - Get instant code feedback before committing
- **Code Reviewers** - Automate repetitive review tasks
- **Team Leads** - Monitor code quality across projects
- **Students** - Learn Python best practices through automated feedback

---

## 2. System Overview

### 2.1 Architecture

The system consists of three main components:

1. **Backend API** (FastAPI)
   - RESTful API endpoints
   - Agent orchestration
   - Database management
   - External integrations

2. **Web Dashboard** (Streamlit)
   - User interface
   - Review history
   - Analytics and metrics
   - Real-time monitoring

3. **Multi-Agent System**
   - Quality Agent
   - Security Agent
   - Performance Agent
   - Documentation Agent

### 2.2 System Requirements

**Minimum Requirements:**
- Python 3.9 or higher
- 4GB RAM
- 2GB free disk space
- Internet connection (for GitHub/GitLab access)

**Recommended:**
- Python 3.11+
- 8GB RAM
- Docker and Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis (optional, for caching)

---

## 3. Installation Guide

### 3.1 Prerequisites

Before installing, ensure you have:

- ✅ Python 3.9+ installed
- ✅ pip (Python package manager)
- ✅ Git
- ✅ Docker and Docker Compose (recommended)
- ✅ PostgreSQL 15+ (if not using Docker)
- ✅ Redis (optional, if not using Docker)

### 3.2 Step-by-Step Installation

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd AdvancedProgramming
```

#### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI and Uvicorn
- Streamlit
- SQLAlchemy
- PyGithub
- LangChain
- Static analysis tools (pylint, flake8, bandit, radon)

#### Step 4: Set Up Environment Variables

Create or edit `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/code_review_db

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# LLM Provider (ollama or openai)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# OpenAI Configuration (if using OpenAI)
# OPENAI_API_KEY=your_api_key_here

# GitHub Configuration (Optional)
GITHUB_TOKEN=your_github_token_here

# Application Settings
APP_NAME=AI Code Review Agent
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO
```

#### Step 5: Set Up Database

**Option A: Using Docker (Recommended)**

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify containers are running
docker-compose ps
```

**Option B: Manual Installation**

**PostgreSQL:**
```bash
# Windows (Chocolatey)
choco install postgresql

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Mac
brew install postgresql

# Create database
createdb code_review_db
```

**Redis (Optional):**
```bash
# Windows (Chocolatey)
choco install redis-64

# Linux (Ubuntu/Debian)
sudo apt-get install redis-server

# Mac
brew install redis

# Start Redis
redis-server
```

#### Step 6: Initialize Database

The database tables will be created automatically when you first start the application.

#### Step 7: Verify Installation

```bash
# Run tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=src --cov-report=term
```

---

## 4. Configuration

### 4.1 LLM Provider Setup

#### Option 1: Ollama (Free, Recommended for Testing)

1. **Install Ollama:**
   - Visit: https://ollama.ai/
   - Download and install for your OS

2. **Pull a Model:**
   ```bash
   ollama pull llama2
   # or
   ollama pull codellama
   ```

3. **Configure in `.env`:**
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2
   ```

4. **Start Ollama:**
   ```bash
   ollama serve
   ```

#### Option 2: OpenAI (Paid)

1. **Get API Key:**
   - Visit: https://platform.openai.com/api-keys
   - Create a new API key

2. **Configure in `.env`:**
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-api-key-here
   ```

### 4.2 GitHub Token Setup

1. **Generate Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Generate and copy the token

2. **Add to `.env`:**
   ```env
   GITHUB_TOKEN=ghp_your_token_here
   ```

**Note:** Without a GitHub token, you can only review local files.

### 4.3 Static Analysis Tools

The system automatically uses these tools (installed via pip):
- **pylint** - Code quality checking
- **flake8** - PEP 8 style enforcement
- **bandit** - Security vulnerability scanning
- **radon** - Code complexity analysis

No additional configuration needed - they work out of the box!

---

## 5. Getting Started

### 5.1 Starting the Application

#### Start Backend API

**Terminal 1:**
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate      # Linux/Mac

# Start backend
python run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### Start Web Dashboard

**Terminal 2:**
```bash
# Activate virtual environment (if not already)
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate      # Linux/Mac

# Start dashboard
python run_dashboard.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 5.2 Access Points

Once both services are running:

- **API Base URL:** http://localhost:8000
- **API Documentation (Swagger):** http://localhost:8000/docs
- **API Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Web Dashboard:** http://localhost:8501
- **Health Check:** http://localhost:8000/api/v1/health

### 5.3 First Test

**Test Health Endpoint:**
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-24T10:30:00",
  "version": "1.0.0"
}
```

**Test Dashboard:**
1. Open browser: http://localhost:8501
2. You should see the dashboard interface
3. Navigate to "New Review" page

---

## 6. Using the Web Dashboard

### 6.1 Dashboard Overview

The dashboard provides a user-friendly interface with the following pages:

1. **Home** - Overview and quick stats
2. **New Review** - Create a new code review
3. **Review History** - View past reviews
4. **Analytics** - Statistics and metrics

### 6.2 Creating a Review

#### Step 1: Navigate to "New Review"

Click on "New Review" in the sidebar.

#### Step 2: Fill Review Form

**Required Fields:**
- **Repository URL** (optional for local files)
  - Example: `https://github.com/owner/repo`
  - Leave empty for local file review

- **File Path** (recommended)
  - Example: `src/main.py`
  - For local files: `test_code_sample.py`
  - Must be relative to repository root

**Optional Fields:**
- **Commit SHA** - Review specific commit
  - Example: `abc123def456...`
  
- **Pull Request ID** - Review PR files
  - Example: `5` (just the number)

- **Agent Types** - Select specific agents
  - Leave empty for all agents
  - Options: Quality, Security, Performance, Documentation

#### Step 3: Start Review

Click **"Start Review"** button.

#### Step 4: View Results

After processing (usually 10-30 seconds), you'll see:
- ✅ Review status
- 📊 Agent results (Quality, Security, Performance, Documentation)
- 🐛 Issues found (with severity levels)
- 💡 Suggestions for improvement
- 📈 Statistics

### 6.3 Review History

**Access:** Click "Review History" in sidebar

**Features:**
- List of all past reviews
- Filter by repository, date, status
- View detailed results
- Delete reviews

**Actions:**
- Click on a review to see details
- Use filters to find specific reviews
- Export results (coming soon)

### 6.4 Analytics

**Access:** Click "Analytics" in sidebar

**Metrics Displayed:**
- Total reviews count
- Issues by severity (Critical, High, Medium, Low)
- Agent performance statistics
- Repository statistics
- Recent reviews (last 7 days)
- Success rate

**Charts:**
- Severity distribution (pie chart)
- Issues over time (line chart)
- Agent comparison (bar chart)

### 6.5 Common Dashboard Scenarios

#### Scenario 1: Review Single File from GitHub

```
Repository URL: https://github.com/python/cpython
File Path: Lib/os.py
Commit SHA: (empty)
Pull Request ID: (empty)
Agent Types: (empty - all agents)
```

#### Scenario 2: Review Local File

```
Repository URL: (empty)
File Path: test_code_sample.py
Commit SHA: (empty)
Pull Request ID: (empty)
Agent Types: (empty)
```

#### Scenario 3: Review Entire Repository

```
Repository URL: https://github.com/owner/repo
File Path: (empty)
Scan Entire Repo: ✅ (check this option)
Commit SHA: (optional)
Agent Types: (empty)
```

#### Scenario 4: Review Directory

```
Repository URL: https://github.com/owner/repo
File Path: src/utils
Commit SHA: (empty)
Pull Request ID: (empty)
Agent Types: (empty)
```

**Note:** Directory path should not end with `.py`

---

## 7. Using the API

### 7.1 API Overview

The REST API provides programmatic access to all features. All endpoints are documented at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 7.2 Authentication

Currently, the API does not require authentication for local use. For production, implement API keys or OAuth.

### 7.3 Core Endpoints

#### 7.3.1 Health Check

**GET** `/api/v1/health`

Check if the API is running.

**Example:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-24T10:30:00",
  "version": "1.0.0"
}
```

#### 7.3.2 Create Review

**POST** `/api/v1/reviews`

Create a new code review.

**Request Body:**
```json
{
  "repository_url": "https://github.com/owner/repo",
  "file_path": "src/main.py",
  "commit_sha": null,
  "pull_request_id": null,
  "agent_types": null,
  "scan_entire_repo": false
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/python/cpython",
    "file_path": "Lib/os.py"
  }'
```

**Response:**
```json
{
  "review_id": 1,
  "repository_url": "https://github.com/python/cpython",
  "file_path": "Lib/os.py",
  "status": "completed",
  "results": [
    {
      "agent_type": "quality",
      "success": true,
      "execution_time": 2.5,
      "issues": [...]
    },
    ...
  ],
  "total_issues": 15,
  "created_at": "2025-12-24T10:30:00",
  "completed_at": "2025-12-24T10:30:05"
}
```

#### 7.3.3 Get Review

**GET** `/api/v1/reviews/{review_id}`

Get details of a specific review.

**Example:**
```bash
curl http://localhost:8000/api/v1/reviews/1
```

#### 7.3.4 List Reviews

**GET** `/api/v1/reviews`

List all reviews with pagination.

**Query Parameters:**
- `limit` - Number of results (default: 10)
- `offset` - Skip results (default: 0)
- `repository_url` - Filter by repository
- `status` - Filter by status (pending, completed, failed)

**Example:**
```bash
curl "http://localhost:8000/api/v1/reviews?limit=20&offset=0"
```

#### 7.3.5 Get Analytics

**GET** `/api/v1/reviews/analytics`

Get review statistics and metrics.

**Example:**
```bash
curl http://localhost:8000/api/v1/reviews/analytics
```

**Response:**
```json
{
  "total_reviews": 50,
  "total_issues": 250,
  "severity_stats": {
    "critical": 5,
    "high": 20,
    "medium": 100,
    "low": 125
  },
  "agent_stats": {...},
  "repo_stats": {...}
}
```

#### 7.3.6 Delete Reviews

**DELETE** `/api/v1/reviews`

Delete all reviews (use with caution).

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/reviews
```

### 7.4 Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Create a review
response = requests.post(
    f"{BASE_URL}/reviews",
    json={
        "repository_url": "https://github.com/owner/repo",
        "file_path": "src/main.py"
    }
)

review = response.json()
print(f"Review ID: {review['review_id']}")
print(f"Total Issues: {review['total_issues']}")

# Get review details
review_id = review['review_id']
response = requests.get(f"{BASE_URL}/reviews/{review_id}")
details = response.json()

# List all reviews
response = requests.get(f"{BASE_URL}/reviews?limit=10")
reviews = response.json()
```

### 7.5 Error Handling

All API errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (review/file not found)
- `500` - Internal Server Error

**Example Error Response:**
```json
{
  "detail": "File 'nonexistent.py' not found in repository."
}
```

---

## 8. Common Use Cases

### 8.1 Use Case 1: Review Before Commit

**Scenario:** You want to check your code before committing.

**Steps:**
1. Save your Python file locally
2. Open Dashboard: http://localhost:8501
3. Go to "New Review"
4. Leave Repository URL empty
5. Enter File Path: `your_file.py`
6. Click "Start Review"
7. Review the issues and fix them
8. Commit your code

### 8.2 Use Case 2: Review Pull Request

**Scenario:** Review all files in a pull request.

**Steps:**
1. Open Dashboard
2. Go to "New Review"
3. Enter Repository URL: `https://github.com/owner/repo`
4. Enter Pull Request ID: `5` (the PR number)
5. Leave File Path empty
6. Click "Start Review"
7. Review all issues across PR files

### 8.3 Use Case 3: Continuous Integration

**Scenario:** Integrate code review into CI/CD pipeline.

**Steps:**
1. Add API call to your CI script:

```bash
#!/bin/bash
REVIEW_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d "{
    \"repository_url\": \"$REPO_URL\",
    \"file_path\": \"$FILE_PATH\"
  }")

TOTAL_ISSUES=$(echo $REVIEW_RESPONSE | jq '.total_issues')

if [ $TOTAL_ISSUES -gt 10 ]; then
  echo "Too many issues found: $TOTAL_ISSUES"
  exit 1
fi
```

2. Set up webhook or scheduled job
3. Fail build if critical issues found

### 8.4 Use Case 4: Code Quality Monitoring

**Scenario:** Monitor code quality over time.

**Steps:**
1. Set up regular reviews (daily/weekly)
2. Use Analytics page to track trends
3. Monitor severity distribution
4. Identify problematic files/repositories
5. Take action based on metrics

### 8.5 Use Case 5: Learning Python Best Practices

**Scenario:** Learn Python best practices through automated feedback.

**Steps:**
1. Write Python code
2. Review it using the system
3. Read suggestions from each agent
4. Understand why issues are flagged
5. Apply fixes and learn patterns
6. Repeat with new code

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Issue 1: "Connection refused" or "Cannot connect to database"

**Symptoms:**
- Backend fails to start
- Database connection errors

**Solutions:**
1. Check if PostgreSQL is running:
   ```bash
   docker ps  # If using Docker
   # or
   pg_isready  # If manual installation
   ```

2. Verify DATABASE_URL in `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/code_review_db
   ```

3. Start PostgreSQL:
   ```bash
   docker-compose up -d postgres
   ```

#### Issue 2: "GitHub token not configured"

**Symptoms:**
- Cannot fetch files from GitHub
- 401 Unauthorized errors

**Solutions:**
1. Check `.env` file has `GITHUB_TOKEN`
2. Verify token is valid (not expired)
3. Restart backend after adding token
4. For local files, you don't need a token

#### Issue 3: "File not found" (404)

**Symptoms:**
- 404 errors when fetching files
- "File not found in repository" message

**Solutions:**
1. Verify file path is correct (relative to repo root)
2. Check file exists in repository
3. Ensure repository URL is correct
4. Try using full file path from repository root

#### Issue 4: "LLM not initialized"

**Symptoms:**
- LLM suggestions not appearing
- "LLM not initialized" in logs

**Solutions:**
1. **For Ollama:**
   - Ensure Ollama is running: `ollama serve`
   - Check model is installed: `ollama list`
   - Verify `.env` settings

2. **For OpenAI:**
   - Check API key is valid
   - Verify account has credits
   - Check rate limits

3. **Disable LLM (if not needed):**
   - System works without LLM
   - Static analysis still works

#### Issue 5: "Port already in use"

**Symptoms:**
- Cannot start backend/dashboard
- Port 8000 or 8501 already in use

**Solutions:**
1. Find process using port:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. Kill the process or change port in `run.py`

#### Issue 6: Static Analysis Tools Not Working

**Symptoms:**
- No issues found from static analysis
- Import errors for pylint/flake8

**Solutions:**
1. Reinstall tools:
   ```bash
   pip install pylint flake8 bandit radon --force-reinstall
   ```

2. Check Python version (3.9+ required)

3. Verify tools are in PATH:
   ```bash
   pylint --version
   flake8 --version
   ```

#### Issue 7: Dashboard Not Loading

**Symptoms:**
- Blank page or errors
- Cannot connect to dashboard

**Solutions:**
1. Check dashboard is running:
   ```bash
   python run_dashboard.py
   ```

2. Verify backend is running (dashboard needs API)

3. Check browser console for errors

4. Try different browser or clear cache

### 9.2 Debug Mode

Enable debug mode for detailed logs:

**In `.env`:**
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

**Restart services** to apply changes.

### 9.3 Getting Help

1. **Check Logs:**
   - Backend logs in terminal
   - Dashboard logs in terminal
   - Check for error messages

2. **Verify Configuration:**
   - `.env` file settings
   - Database connection
   - External services (GitHub, LLM)

3. **Test Components:**
   ```bash
   # Test API
   curl http://localhost:8000/api/v1/health
   
   # Test database
   python -c "from src.database.connection import engine; print(engine)"
   
   # Run tests
   pytest tests/ -v
   ```

4. **Common Solutions:**
   - Restart all services
   - Reinstall dependencies
   - Check system requirements
   - Verify network connectivity

---

## 10. Advanced Features

### 10.1 Repository Scanning

Scan entire repositories for all Python files:

**Via Dashboard:**
- Check "Scan Entire Repo" option
- Leave File Path empty
- System will find all `.py` files

**Via API:**
```json
{
  "repository_url": "https://github.com/owner/repo",
  "scan_entire_repo": true
}
```

**Limits:**
- Maximum 50 files processed per scan (performance)
- Large repositories may take time

### 10.2 Directory Scanning

Scan specific directories:

**Via Dashboard:**
- Enter directory path (e.g., `src/utils`)
- Don't include `.py` extension
- System recursively finds all Python files

**Via API:**
```json
{
  "repository_url": "https://github.com/owner/repo",
  "file_path": "src/utils"
}
```

### 10.3 Selective Agent Execution

Run only specific agents:

**Via Dashboard:**
- Select agent types from dropdown
- Options: Quality, Security, Performance, Documentation

**Via API:**
```json
{
  "repository_url": "https://github.com/owner/repo",
  "file_path": "src/main.py",
  "agent_types": ["quality", "security"]
}
```

### 10.4 Commit-Specific Review

Review code at specific commit:

**Via Dashboard:**
- Enter Commit SHA in "Commit SHA" field
- Example: `abc123def456...`

**Via API:**
```json
{
  "repository_url": "https://github.com/owner/repo",
  "file_path": "src/main.py",
  "commit_sha": "abc123def456..."
}
```

### 10.5 Pull Request Review

Review all files in a pull request:

**Via Dashboard:**
- Enter Pull Request ID (just the number)
- Leave File Path empty

**Via API:**
```json
{
  "repository_url": "https://github.com/owner/repo",
  "pull_request_id": 5
}
```

**Note:** Only Python files in the PR are reviewed.

---

## 11. FAQ

### Q1: Do I need a GitHub token?

**A:** Only if you want to review files from GitHub repositories. For local files, no token is needed.

### Q2: Can I use GitLab instead of GitHub?

**A:** Currently, GitHub is fully supported. GitLab support is planned but not yet complete.

### Q3: How long does a review take?

**A:** Typically 10-30 seconds for a single file, depending on:
- File size
- Number of agents
- LLM response time
- Static analysis complexity

### Q4: What Python versions are supported?

**A:** Python 3.9 and higher. The system itself requires Python 3.9+.

### Q5: Can I review non-Python files?

**A:** Currently, only Python (`.py`) files are supported.

### Q6: Is the LLM required?

**A:** No. The system works without LLM. Static analysis tools will still work.

### Q7: How do I increase review speed?

**A:** 
- Use fewer agents (select specific ones)
- Disable LLM (if not needed)
- Review smaller files
- Use local files instead of GitHub

### Q8: Can I integrate this into CI/CD?

**A:** Yes! Use the REST API in your CI scripts. See Section 8.3 for examples.

### Q9: What's the difference between agents?

**A:**
- **Quality Agent:** Code style, PEP 8, best practices
- **Security Agent:** Vulnerabilities, secrets, SQL injection
- **Performance Agent:** Complexity, bottlenecks, optimization
- **Documentation Agent:** Docstrings, comments, documentation quality

### Q10: How accurate are the suggestions?

**A:** 
- Static analysis tools are highly accurate
- LLM suggestions are contextual but may need human review
- Always review critical security issues manually

### Q11: Can I customize agent behavior?

**A:** Currently, agent behavior is fixed. Customization is planned for future versions.

### Q12: What if I find a bug?

**A:** 
- Check Troubleshooting section (Section 9)
- Review logs for error messages
- Verify configuration
- Report issues to the development team

### Q13: Is there a limit on file size?

**A:** No hard limit, but very large files (>5000 lines) may take longer to process.

### Q14: Can I review private repositories?

**A:** Yes, if you have a GitHub token with `repo` scope.

### Q15: How do I update the system?

**A:**
```bash
git pull
pip install -r requirements.txt --upgrade
# Restart services
```

---

## 📞 Support

For additional help:
- Check the documentation
- Review troubleshooting section
- Check project README
- Contact course instructor

---

## 📝 Version History

- **v1.0.0** (December 2025)
  - Initial release
  - Multi-agent system
  - GitHub integration
  - Web dashboard
  - REST API
  - 90% test coverage

---

**End of User Manual**

*Last Updated: December 2025*  
*Course: SEN0414 Advanced Programming*  
*Istanbul Kültür University - Computer Engineering Department*


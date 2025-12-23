# AI-Powered Code Review Agent

A sophisticated multi-agent system designed to autonomously review Python code for quality, security, performance, and best practices. This system integrates with GitHub/GitLab repositories, leverages static analysis tools, and utilizes Large Language Models (LLMs) to provide intelligent, context-aware code review suggestions.

## 🚀 Features

- **Multi-Agent Architecture**: Four specialized agents (Quality, Security, Performance, Documentation) working in parallel
- **GitHub/GitLab Integration**: Direct integration with popular version control platforms
- **Static Analysis Integration**: Combines results from pylint, flake8, bandit, and radon
- **LLM-Powered Analysis**: Intelligent code understanding using OpenAI/Claude or free alternatives (Ollama)
- **Web Dashboard**: Real-time analytics and review history visualization
- **Learning System**: Adapts and improves based on feedback and historical data

## 📋 Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 15+ (or use Docker)
- Redis (or use Docker)
- GitHub/GitLab API token (optional, for repository access)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/baslarbatuhan/ai-code-review-agent.git
cd ai-code-review-agent
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/code_review_db
REDIS_URL=redis://localhost:6379/0
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
GITHUB_TOKEN=your_github_token_here
```

### 5. Set up database

```bash
# Using Docker Compose (recommended)
docker-compose up -d postgres redis

# Or manually create PostgreSQL database
createdb code_review_db
```

### 6. Initialize database tables

The tables will be created automatically when you start the application.

## 🚀 Running the Application

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI backend (port 8000)
- Streamlit dashboard (port 8501)

### Option 2: Manual Start

#### Start Backend API

```bash
cd src
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Dashboard

```bash
streamlit run dashboard/main.py
```

## 📖 Usage

### API Endpoints

#### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

#### Create Review

```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/owner/repo",
    "file_path": "src/main.py"
  }'
```

#### Get Review

```bash
curl http://localhost:8000/api/v1/reviews/{review_id}
```

### Web Dashboard

Access the dashboard at: http://localhost:8501

1. Navigate to "New Review"
2. Enter repository URL
3. Optionally specify file path, commit SHA, or PR ID
4. Select agent types (or leave empty for all)
5. Click "Start Review"

## 🏗️ Project Structure

```
.
├── src/
│   ├── agents/          # Agent implementations
│   │   ├── base_agent.py
│   │   ├── quality_agent.py
│   │   ├── security_agent.py
│   │   ├── performance_agent.py
│   │   └── documentation_agent.py
│   ├── api/             # FastAPI application
│   │   ├── main.py
│   │   └── routes/
│   ├── core/            # Core functionality
│   │   ├── orchestrator.py
│   │   └── schemas.py
│   ├── database/        # Database models
│   │   ├── models.py
│   │   └── connection.py
│   ├── integrations/    # External integrations
│   │   ├── github.py
│   │   └── llm.py
│   └── utils/           # Utility functions
│       └── static_analysis.py
├── dashboard/           # Streamlit dashboard
│   └── main.py
├── tests/               # Test suite
├── config/              # Configuration
│   └── settings.py
├── docker/              # Docker files
├── docs/                # Documentation
│   ├── USER_MANUAL.md
│   ├── INSTALL.md
│   ├── QUICKSTART.md
│   ├── DASHBOARD_USAGE_GUIDE.md
│   └── GITHUB_TOKEN_SETUP.md
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🧪 Testing

Run tests:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Configuration

### LLM Providers

#### Ollama (Free, Local)

1. Install Ollama: https://ollama.ai/
2. Pull a model:
   ```bash
   ollama pull llama2
   ```
3. Set in `.env`:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2
   ```

#### OpenAI (Paid)

Set in `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

## 📊 Static Analysis Tools

The system integrates with:

- **pylint**: Code quality and style checking
- **flake8**: PEP 8 style guide enforcement
- **bandit**: Security vulnerability scanning
- **radon**: Code complexity analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is developed for academic purposes as part of SEN0414 Advanced Programming course.

## 👥 Authors

- [Your Name] - [Student ID] - [Role]
- [Team Member 2] - [Student ID] - [Role]
- [Team Member 3] - [Student ID] - [Role]

**Note:** Please update with actual team member information.

## 🙏 Acknowledgments

- Istanbul Kültür University - Computer Engineering Department
- Course Instructor: Yusuf Altunel
- AI4SE Framework

## 📚 Documentation

- [User Manual](docs/USER_MANUAL.md) - Complete user guide
- [Installation Guide](docs/INSTALL.md) - Detailed installation instructions
- [Quick Start Guide](docs/QUICKSTART.md) - Get started in 3 steps
- [Dashboard Usage Guide](docs/DASHBOARD_USAGE_GUIDE.md) - Dashboard instructions
- [GitHub Token Setup](docs/GITHUB_TOKEN_SETUP.md) - GitHub integration setup
- [API Documentation](http://localhost:8000/docs) - Swagger UI (when running)

## ⚠️ Known Issues

- Some static analysis tools may require additional system dependencies
- LLM integration requires Ollama or OpenAI API key
- GitHub rate limiting may affect testing

## 🔮 Future Improvements

- [ ] GitLab integration completion
- [ ] Advanced learning system with ML models
- [ ] Real-time review notifications
- [ ] CI/CD integration plugins
- [ ] Multi-language support (beyond Python)

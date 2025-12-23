# Installation Guide

Detaylı kurulum kılavuzu.

## Gereksinimler

- Python 3.9 veya üzeri
- pip (Python paket yöneticisi)
- Git
- Docker ve Docker Compose (opsiyonel, önerilen)
- PostgreSQL 15+ (Docker kullanmıyorsanız)
- Redis (Docker kullanmıyorsanız)

## Adım Adım Kurulum

### 1. Projeyi Klonla

```bash
git clone <repository-url>
cd AdvancedProgramming
```

### 2. Python Versiyonunu Kontrol Et

```bash
python --version
# Python 3.9+ olmalı
```

### 3. Virtual Environment Oluştur

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 4. Bağımlılıkları Yükle

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Bu işlem birkaç dakika sürebilir.

### 5. Ortam Değişkenlerini Ayarla

`.env` dosyası zaten oluşturuldu. Gerekirse düzenleyin:

```bash
# .env dosyasını aç
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Minimum yapılandırma:**

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/code_review_db
REDIS_URL=redis://localhost:6379/0
LLM_PROVIDER=ollama
```

### 6. Database Kurulumu

#### Seçenek A: Docker ile (Önerilen)

```bash
# PostgreSQL ve Redis'i başlat
docker-compose up -d postgres redis

# Durumu kontrol et
docker-compose ps
```

#### Seçenek B: Manuel Kurulum

**PostgreSQL:**

```bash
# Windows (Chocolatey)
choco install postgresql

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Mac
brew install postgresql

# Database oluştur
createdb code_review_db
```

**Redis:**

```bash
# Windows (Chocolatey)
choco install redis-64

# Linux (Ubuntu/Debian)
sudo apt-get install redis-server

# Mac
brew install redis

# Redis'i başlat
redis-server
```

### 7. LLM Kurulumu (Opsiyonel)

#### Ollama (Önerilen - Ücretsiz)

```bash
# Ollama'yı indir ve kur: https://ollama.ai/

# Model indir
ollama pull llama2

# .env dosyasında ayarla
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### OpenAI (Ücretli)

```bash
# .env dosyasında ayarla
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

### 8. GitHub Token (Opsiyonel)

GitHub API kullanmak için:

1. GitHub'a git: https://github.com/settings/tokens
2. "Generate new token" tıkla
3. `repo` scope'unu seç
4. Token'ı kopyala
5. `.env` dosyasına ekle: `GITHUB_TOKEN=your_token_here`

### 9. Uygulamayı Başlat

```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Dashboard
python run_dashboard.py
```

### 10. Test Et

Tarayıcıda aç:
- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

## Doğrulama

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Beklenen çıktı:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-23T...",
  "version": "1.0.0"
}
```

### Test Suite

```bash
pytest tests/ -v
```

## Sorun Giderme

### Port Zaten Kullanılıyor

```bash
# Port'u değiştir
# run.py içinde port=8000 -> port=8001
# veya
# .env dosyasında API_PORT=8001
```

### Database Bağlantı Hatası

```bash
# PostgreSQL çalışıyor mu kontrol et
docker ps  # Docker kullanıyorsanız
# veya
pg_isready  # Manuel kurulum

# Bağlantı string'ini kontrol et
# .env dosyasındaki DATABASE_URL
```

### ModuleNotFoundError

```bash
# Virtual environment aktif mi?
which python  # Linux/Mac
where python   # Windows

# Bağımlılıkları tekrar yükle
pip install -r requirements.txt --force-reinstall
```

### Static Analysis Tools Hatası

Bazı araçlar sistem bağımlılıkları gerektirir:

```bash
# Windows
choco install python3

# Linux
sudo apt-get install python3-dev build-essential

# Mac
xcode-select --install
```

## Sonraki Adımlar

- [QUICKSTART.md](QUICKSTART.md) - Hızlı başlangıç
- [README.md](README.md) - Genel dokümantasyon
- [Project1_AI_Code_Review_Agent_Proposal.md](Project1_AI_Code_Review_Agent_Proposal.md) - Proje detayları


# Quick Start Guide

Bu kılavuz projeyi hızlıca çalıştırmak için adım adım talimatlar içerir.

## 🚀 Hızlı Başlangıç (3 Adım)

### 1. Virtual Environment Oluştur ve Bağımlılıkları Yükle

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Linux/Mac
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Ortam Değişkenlerini Ayarla

`.env` dosyası zaten oluşturuldu. Gerekirse düzenleyin:

```bash
# .env dosyasını düzenle
notepad .env  # Windows
# veya
nano .env     # Linux/Mac
```

**Önemli:** Eğer GitHub API kullanacaksanız, `GITHUB_TOKEN` değerini ayarlayın.

### 3. Uygulamayı Çalıştır

#### Seçenek A: Docker ile (Önerilen)

```bash
# PostgreSQL ve Redis'i başlat
docker-compose up -d postgres redis

# Backend'i çalıştır (yeni terminal)
python run.py

# Dashboard'u çalıştır (başka bir terminal)
python run_dashboard.py
```

#### Seçenek B: Manuel (PostgreSQL ve Redis kurulu olmalı)

```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Dashboard
python run_dashboard.py
```

## 📍 Erişim Adresleri

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501

## 🧪 Test Etme

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Belirli bir test dosyası
pytest tests/test_agents.py -v
```

## ⚠️ Sorun Giderme

### PostgreSQL Bağlantı Hatası

Eğer PostgreSQL yüklü değilse:

```bash
# Docker ile PostgreSQL başlat
docker-compose up -d postgres

# Veya SQLite kullan (geliştirme için)
# config/settings.py'de DATABASE_URL'i değiştir:
# DATABASE_URL=sqlite:///./code_review.db
```

### Import Hataları

```bash
# Virtual environment aktif mi kontrol et
which python  # Linux/Mac
where python   # Windows

# Bağımlılıkları tekrar yükle
pip install -r requirements.txt --upgrade
```

### Static Analysis Tools Hatası

Bazı static analysis tools sistem bağımlılıkları gerektirebilir:

```bash
# Windows (Chocolatey ile)
choco install python3

# Linux (Ubuntu/Debian)
sudo apt-get install python3-dev

# Mac
brew install python3
```

## 📝 İlk Kullanım

1. Dashboard'u aç: http://localhost:8501
2. "New Review" sayfasına git
3. Bir GitHub repository URL'i gir (örn: `https://github.com/python/cpython`)
4. Bir Python dosyası yolu gir (örn: `Lib/os.py`)
5. "Start Review" butonuna tıkla

**Not:** İlk kullanımda GitHub token gerekebilir. Token olmadan sadece yerel dosyaları test edebilirsiniz.

## 🔧 Geliştirme Modu

```bash
# Backend'i reload modunda çalıştır
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Dashboard'u otomatik reload ile
streamlit run dashboard/main.py --server.runOnSave true
```

## 📚 Sonraki Adımlar

- [README.md](README.md) - Detaylı dokümantasyon
- [Project1_AI_Code_Review_Agent_Proposal.md](Project1_AI_Code_Review_Agent_Proposal.md) - Proje önerisi
- API dokümantasyonu: http://localhost:8000/docs


# 🔑 GitHub Token Kurulumu

GitHub repository'lerinden kod çekmek için GitHub token gerekiyor.

## 🚀 Hızlı Kurulum (5 dakika)

### Adım 1: GitHub Token Oluştur

1. GitHub'a git: https://github.com/settings/tokens
2. "Generate new token" → "Generate new token (classic)" tıkla
3. Token ayarları:
   - **Note**: `AI Code Review Agent` (açıklama)
   - **Expiration**: İstediğiniz süre (90 gün önerilir)
   - **Scopes**: `repo` seçin (tüm repo erişimi için)
4. "Generate token" butonuna tıkla
5. **Token'ı kopyala** (bir daha gösterilmeyecek!)

### Adım 2: Token'ı Projeye Ekle

#### Seçenek A: .env Dosyası (Önerilen)

1. Proje kök dizininde `.env` dosyası oluştur (eğer yoksa)
2. Şu satırı ekle:

```env
GITHUB_TOKEN=ghp_your_token_here
```

**Örnek:**
```env
GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz
```

#### Seçenek B: config/settings.py (Geçici)

`config/settings.py` dosyasında:

```python
github_token: Optional[str] = "ghp_your_token_here"
```

**⚠️ UYARI:** Bu yöntem güvenli değil! Token'ı commit etmeyin!

### Adım 3: Uygulamayı Yeniden Başlat

1. Backend'i durdur (CTRL+C)
2. Tekrar başlat: `python run.py`

### Adım 4: Test Et

Dashboard'da:
1. Repository URL: `https://github.com/owner/repo`
2. File Path: `src/main.py`
3. "Start Review" tıkla

✅ Başarılı ise: Kod çekilecek ve inceleme yapılacak

## 🔒 Güvenlik Notları

### ✅ Yapılması Gerekenler

- ✅ Token'ı `.env` dosyasında sakla
- ✅ `.env` dosyasını `.gitignore`'a ekle (zaten ekli)
- ✅ Token'ı asla commit etme
- ✅ Token'ı paylaşma

### ❌ Yapılmaması Gerekenler

- ❌ Token'ı kod içine yazma
- ❌ Token'ı GitHub'a commit etme
- ❌ Token'ı public repository'de paylaşma
- ❌ Token'ı screenshot'larda gösterme

## 🧪 Token'ı Test Etme

### Yöntem 1: API ile Test

```powershell
.\venv\Scripts\Activate.ps1
python -c "
from src.integrations.github import GitHubIntegration
github = GitHubIntegration()
try:
    repo = github.get_repository('python/cpython')
    print('✓ GitHub token çalışıyor!')
except Exception as e:
    print(f'✗ Hata: {e}')
"
```

### Yöntem 2: Dashboard ile Test

1. Dashboard'u aç: http://localhost:8501
2. Repository URL gir: `https://github.com/python/cpython`
3. File Path gir: `Lib/os.py`
4. "Start Review" tıkla

✅ Başarılı ise: Kod çekilecek ve inceleme başlayacak

## 🐛 Sorun Giderme

### Problem: "GitHub token not configured"

**Çözüm:**
1. `.env` dosyasının var olduğundan emin ol
2. Token'ın doğru formatta olduğundan emin (`ghp_` ile başlamalı)
3. Uygulamayı yeniden başlat

### Problem: "Bad credentials"

**Çözüm:**
1. Token'ın geçerli olduğundan emin
2. Token'ın `repo` scope'una sahip olduğundan emin
3. Token'ın expire olmadığından emin

### Problem: "Not found"

**Çözüm:**
1. Repository URL'in doğru olduğundan emin
2. Repository'nin public olduğundan veya token'ın erişim yetkisi olduğundan emin

## 📝 Alternatif: Yerel Dosya Kullan

GitHub token olmadan da çalışabilirsiniz! Yerel dosyaları inceleyebilirsiniz:

1. Dashboard'da "Repository URL" alanını **boş bırakın**
2. "File Path" alanına yerel dosya yolunu girin: `test_code_sample.py`
3. "Start Review" tıkla

✅ Yerel dosyalar token gerektirmez!

## 🎯 Özet

1. ✅ GitHub token oluştur (https://github.com/settings/tokens)
2. ✅ `.env` dosyasına ekle: `GITHUB_TOKEN=ghp_...`
3. ✅ Uygulamayı yeniden başlat
4. ✅ Test et

Artık GitHub repository'lerinden kod çekebilirsiniz! 🚀


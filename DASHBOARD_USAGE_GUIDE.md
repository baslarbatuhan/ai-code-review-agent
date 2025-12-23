# 📖 Dashboard Kullanım Kılavuzu

## 🎯 Doğru Kullanım

### Senaryo 1: GitHub Repository'den Dosya İnceleme (Önerilen)

1. **Repository URL**: `https://github.com/baslarbatuhan/Stock-Market-Portfolio`
2. **File Path**: `src/main.py` (veya başka bir Python dosyası)
3. **Commit SHA**: Boş bırakın
4. **Pull Request ID**: Boş bırakın (veya 0 yapın)
5. **Agent Types**: Boş bırakın (tüm agent'lar çalışır)

✅ **"Start Review"** butonuna tıklayın

### Senaryo 2: Yerel Dosya İnceleme

1. **Repository URL**: Boş bırakın veya `local` yazın
2. **File Path**: `test_code_sample.py` (yerel dosya yolu)
3. **Commit SHA**: Boş bırakın
4. **Pull Request ID**: Boş bırakın
5. **Agent Types**: Boş bırakın

✅ **"Start Review"** butonuna tıklayın

### Senaryo 3: Pull Request İnceleme

1. **Repository URL**: `https://github.com/owner/repo`
2. **File Path**: Boş bırakın
3. **Commit SHA**: Boş bırakın
4. **Pull Request ID**: Gerçek PR numarası (örn: 5, 10, 23)
5. **Agent Types**: Boş bırakın

⚠️ **ÖNEMLİ**: PR numarasının doğru olduğundan emin olun!

### Senaryo 4: Commit İnceleme

1. **Repository URL**: `https://github.com/owner/repo`
2. **File Path**: Boş bırakın
3. **Commit SHA**: Gerçek commit SHA (örn: `abc123def456...`)
4. **Pull Request ID**: Boş bırakın
5. **Agent Types**: Boş bırakın

## ❌ Yaygın Hatalar

### Hata 1: Pull Request Bulunamadı (404)

**Hata Mesajı:**
```
Error: {"detail":"Error fetching code: 404 Not Found"}
```

**Neden:**
- Pull Request ID yanlış veya repository'de böyle bir PR yok
- Hem File Path hem Pull Request ID dolu (çakışma)

**Çözüm:**
- ✅ **File Path kullanın** (Pull Request ID'yi boş bırakın)
- ✅ Veya doğru Pull Request ID'yi girin
- ✅ Sadece birini kullanın: File Path VEYA Pull Request ID VEYA Commit SHA

### Hata 2: GitHub Token Hatası

**Hata Mesajı:**
```
Error: {"detail":"Error fetching code: GitHub token not configured"}
```

**Çözüm:**
- `.env` dosyasında `GITHUB_TOKEN` olduğundan emin olun
- Backend'i yeniden başlatın

### Hata 3: Dosya Bulunamadı

**Hata Mesajı:**
```
Error: {"detail":"Error fetching code: 404 Not Found"}
```

**Çözüm:**
- File Path'in doğru olduğundan emin olun
- Repository'de bu dosyanın var olduğundan emin olun
- Dosya yolunun repository root'una göre olduğundan emin olun

## 📋 Öncelik Sırası

Sistem şu sırayla çalışır:

1. **File Path** (en yüksek öncelik)
   - Repository URL + File Path → Dosyayı direkt çeker
   
2. **Commit SHA**
   - Repository URL + Commit SHA → Commit'teki dosyaları çeker
   
3. **Pull Request ID** (en düşük öncelik)
   - Repository URL + Pull Request ID → PR'deki dosyaları çeker

## 💡 İpuçları

### ✅ En Kolay Yöntem

**Sadece File Path kullanın:**
- Repository URL: `https://github.com/owner/repo`
- File Path: `src/main.py`
- Diğer alanlar: Boş

Bu en güvenilir yöntemdir!

### ✅ Yerel Dosya Test

GitHub token olmadan test etmek için:
- Repository URL: Boş
- File Path: `test_code_sample.py`
- Diğer alanlar: Boş

### ✅ PR Numarasını Bulma

GitHub'da repository'ye gidin:
1. "Pull requests" sekmesine tıklayın
2. PR numarasını görün (örn: #5, #10)
3. Sadece numarayı girin (5, 10)

## 🎯 Örnek Kullanım

### Örnek 1: Basit Dosya İnceleme
```
Repository URL: https://github.com/python/cpython
File Path: Lib/os.py
Commit SHA: (boş)
Pull Request ID: (boş)
```

### Örnek 2: Yerel Test
```
Repository URL: (boş)
File Path: test_code_sample.py
Commit SHA: (boş)
Pull Request ID: (boş)
```

### Örnek 3: PR İnceleme (Doğru)
```
Repository URL: https://github.com/owner/repo
File Path: (boş)
Commit SHA: (boş)
Pull Request ID: 5  (gerçek PR numarası)
```

## 🐛 Sorun Giderme

### Problem: "404 Not Found"

**Kontrol Listesi:**
1. ✅ Repository URL doğru mu?
2. ✅ File Path doğru mu? (repository root'una göre)
3. ✅ Pull Request ID gerçekten var mı?
4. ✅ Commit SHA doğru mu?

### Problem: "GitHub token not configured"

**Çözüm:**
1. `.env` dosyasını kontrol edin
2. Backend'i yeniden başlatın
3. Token'ın geçerli olduğundan emin olun

### Problem: "No Python files found"

**Çözüm:**
- PR veya Commit'te Python dosyası yok
- File Path kullanmayı deneyin

## ✨ Başarı İşaretleri

✅ **Başarılı ise göreceksiniz:**
- "Review completed!" mesajı
- Agent sonuçları (Quality, Security, Performance, Documentation)
- Issues listesi
- Suggestions

🎉 **Artık kod incelemesi yapabilirsiniz!**


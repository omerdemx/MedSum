# MedSum (MedInsight) - Tıbbi Literatür Analiz Platformu

MedSum, tıbbi ve akademik literatürü arayan, Türkçe'ye çeviren, özetleyen ve klinik önemli çıkarımları çıkaran modern bir web platformudur. Araştırmacılar, tıp öğrencileri ve klinisyenler için tasarlanmıştır.

## 🎯 Özellikler

### 🔍 Çoklu Kaynak Arama
- **arXiv**: Tamamen ücretsiz, API key gerektirmez
- **Europe PMC**: Ücretsiz, API key gerektirmez
- **DOAJ**: Ücretsiz, API key gerektirmez
- **Semantic Scholar**: Opsiyonel (API key ile)
- Paralel arama ile hızlı sonuçlar
- Otomatik tekrar kaldırma (duplicate detection)

### 🤖 AI Destekli NLP İşlemleri
- **Otomatik Çeviri**: Başlık ve abstract'lerin İngilizce'den Türkçe'ye çevirisi
- **Akıllı Özetleme**: 2-3 cümlelik Türkçe özetler
- **Klinik Çıkarımlar**: Her makale için 3 adet klinik önemli çıkarım
- OpenAI GPT-3.5-turbo modeli kullanımı
- Token optimizasyonu ile maliyet kontrolü

### 💻 Modern Web Arayüzü
- React 19 ile geliştirilmiş responsive tasarım
- Kullanıcı dostu arama formu
- Detaylı makale kartları
- Genişletilebilir içerik görünümü
- Yükleme durumu ve hata yönetimi

### ⚡ Performans
- Asenkron işlemler ile hızlı yanıt süreleri
- Paralel API çağrıları
- Optimize edilmiş token kullanımı

## 📋 Gereksinimler

### Backend
- Python 3.8+
- OpenAI API Key
- (Opsiyonel) Semantic Scholar API Key

### Frontend
- Node.js 16+
- npm veya yarn

## 🚀 Kurulum

### 1. Projeyi Klonlayın

```bash
git clone <repository-url>
cd MedSum
```

### 2. Backend Kurulumu

```bash
# Python sanal ortamı oluşturun (önerilir)
python -m venv venv

# Sanal ortamı aktifleştirin
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 3. Ortam Değişkenlerini Ayarlayın

Proje kök dizininde `.env` dosyası oluşturun:

```env
OPENAI_API_KEY=your_openai_api_key_here
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key_here  # Opsiyonel
```

### 4. Frontend Kurulumu

```bash
cd frontend
npm install
```

## 🏃 Çalıştırma

### Backend Sunucusunu Başlatın

```bash
# Proje kök dizininde
python main.py
```

Backend API `http://localhost:8000` adresinde çalışacaktır.

### Frontend Geliştirme Sunucusunu Başlatın

```bash
# frontend dizininde
cd frontend
npm run dev
```

Frontend uygulaması genellikle `http://localhost:5173` adresinde çalışacaktır.

### Production Build

```bash
# Frontend için
cd frontend
npm run build
```

Build edilmiş dosyalar `frontend/dist` dizininde oluşturulacaktır.

## 📖 Kullanım

### API Kullanımı

#### Endpoint: `/api/analyze_articles`

**Method**: `POST`

**Request Body**:
```json
{
  "keyword": "diabetic retinopathy treatment",
  "article_count": 10,
  "time_range_years": 5
}
```

**Response**:
```json
[
  {
    "pmid": "12345678",
    "title_en": "Treatment of Diabetic Retinopathy",
    "title_tr": "Diyabetik Retinopati Tedavisi",
    "authors": ["John Doe", "Jane Smith"],
    "publication_date": "2023-01-15",
    "doi": "10.1234/example",
    "pubmed_url": "https://...",
    "abstract_tr": "Tam çevrilmiş abstract...",
    "summary_tr": "Kısa özet (2-3 cümle)...",
    "key_takeaways_tr": [
      "Çıkarım 1",
      "Çıkarım 2",
      "Çıkarım 3"
    ]
  }
]
```

### Web Arayüzü Kullanımı

1. Anahtar kelime girin (örn: "diabetic retinopathy treatment")
2. Makale sayısını seçin (1-50 arası)
3. (Opsiyonel) Son N yıl filtresi ekleyin
4. "Makale Ara" butonuna tıklayın
5. Sonuçları inceleyin ve detayları görüntüleyin

## 🏗️ Proje Yapısı

```
MedSum/
├── main.py                 # FastAPI ana uygulama
├── config.py              # Yapılandırma ayarları
├── requirements.txt        # Python bağımlılıkları
├── .env                   # Ortam değişkenleri (oluşturulmalı)
│
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic veri modelleri
│
├── services/
│   ├── __init__.py
│   ├── academic_search_service.py  # Akademik arama servisleri
│   ├── nlp_service.py             # NLP işlemleri
│   └── pubmed_service.py           # (Eski) PubMed servisi
│
└── frontend/
    ├── src/
    │   ├── App.jsx        # Ana React bileşeni
    │   ├── components/
    │   │   ├── ArticleCard.jsx
    │   │   ├── ArticleList.jsx
    │   │   ├── LoadingSpinner.jsx
    │   │   └── SearchForm.jsx
    │   └── services/
    │       └── api.js     # API entegrasyonu
    ├── package.json
    └── vite.config.js
```

## 🔧 Yapılandırma

### API Ayarları

`config.py` dosyasında API başlığı, açıklama ve versiyon bilgileri bulunur:

```python
API_TITLE = "MedInsight API"
API_DESCRIPTION = "Tıbbi literatür analiz platformu için backend API"
API_VERSION = "1.0.0"
```

### CORS Ayarları

Production ortamında `main.py` dosyasındaki CORS ayarlarını güncelleyin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Spesifik origin'ler
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Test

### API Sağlık Kontrolü

```bash
curl http://localhost:8000/health
```

### API Endpoint Testi

```bash
curl -X POST http://localhost:8000/api/analyze_articles \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "diabetes",
    "article_count": 5,
    "time_range_years": 3
  }'
```

## 📦 Bağımlılıklar

### Backend
- `fastapi>=0.104.1` - Modern web framework
- `uvicorn[standard]>=0.24.0` - ASGI sunucu
- `openai>=1.3.5` - OpenAI API client
- `httpx>=0.25.2` - Asenkron HTTP client
- `pydantic>=2.5.0` - Veri doğrulama
- `python-dotenv>=1.0.0` - Ortam değişkenleri yönetimi

### Frontend
- `react>=19.2.0` - UI framework
- `axios>=1.13.2` - HTTP client
- `vite>=7.2.4` - Build tool

## 🐛 Sorun Giderme

### Backend Başlatma Sorunları

- **OpenAI API Key Hatası**: `.env` dosyasında `OPENAI_API_KEY` değişkeninin doğru ayarlandığından emin olun
- **Port Kullanımda**: Farklı bir port kullanmak için `main.py` dosyasındaki port numarasını değiştirin

### Frontend Bağlantı Sorunları

- **API Bağlantı Hatası**: `frontend/src/services/api.js` dosyasındaki `API_BASE_URL` değerini kontrol edin
- **CORS Hatası**: Backend'deki CORS ayarlarını kontrol edin

### Arama Sonuçları Boş Geliyor

- Farklı anahtar kelimeler deneyin
- Tarih filtresini kaldırın veya genişletin
- Makale sayısını artırın

## 📝 Lisans

Bu proje [lisans bilgisi] altında lisanslanmıştır.

## 👥 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📧 İletişim

Sorularınız veya önerileriniz için [iletişim bilgisi] üzerinden ulaşabilirsiniz.

## 🙏 Teşekkürler

- OpenAI - GPT-3.5-turbo modeli
- arXiv, Europe PMC, DOAJ, Semantic Scholar - Ücretsiz akademik API'ler
- FastAPI ve React toplulukları

---

**Not**: Bu proje eğitim ve araştırma amaçlıdır. Production kullanımı için ek güvenlik önlemleri ve optimizasyonlar gerekebilir.

## Email OSINT Tool

Flask tabanlı bir Email OSINT aracı. Aşağıdaki bileşenlerden oluşur:
- MX kayıt analizi (DNS)
- İsteğe bağlı BuiltWith teknoloji yığını (API anahtarı ile)
- E‑posta pattern üretimi (isim/soyisim + domain)
- (Opsiyonel) SMTP RCPT probing ile posta kutusu sinyali
- Web arayüzü (form), JSON API ve birim/entegrasyon testleri


### 1) Hızlı Başlangıç (Lokal)
Gereksinimler: Python 3.11+ (3.13 desteklenir), virtualenv önerilir

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Geliştirme sunucusu (hot-reload)
export FLASK_APP=app:app
export FLASK_DEBUG=1
flask run --host 127.0.0.1 --port 5000

# Doğrulama
curl http://127.0.0.1:5000/health
```

Tarayıcı: http://127.0.0.1:5000/


### 2) API ve Arayüz
- Web arayüzü: `/` (form ile domain/email/isim girişi)
- Sağlık kontrolü: `GET /health` → `{ "ok": true }`
- Simülasyon (JSON API): `POST /simulate`
  - Gövde örneği:
    ```json
    { "first_name": "Ada", "last_name": "Lovelace", "domain": "example.com", "use_builtwith": true }
    ```
  - Dönüş: Toplanan verilerin birleşik sözlüğü
- Form işleme: `/analyze` (GET/POST)
  - JSON görüntüleme: `/analyze?domain=example.com&format=json`


### 3) Testler
Unit testler (izole):
```bash
python -m pytest -q
```

Canlı entegrasyon testleri (opsiyonel, env ile açılır):
```bash
# MX
LIVE_MX=1 LIVE_DOMAIN=gmail.com python -m pytest -q tests/test_integrations_live.py::test_mx_analyze_live

# BuiltWith (API anahtarı gerekir)
LIVE_BUILTWITH=1 BUILTWITH_API_KEY=<KEY> LIVE_DOMAIN=github.com \
python -m pytest -q tests/test_integrations_live.py::test_builtwith_live

# SMTP probe (birçok bulut ortamında 25/TCP kısıtlı olabilir)
SMTP_LIVE=1 SMTP_TEST_EMAIL="nopeaddress123456789@gmail.com" SMTP_MAIL_FROM="probe@example.com" \
python -m pytest -q tests/test_integrations_live.py::test_smtp_probe_live
```


### 4) Render ile Deploy
1) Dosyalar ve komutlar
   - `requirements.txt` içinde `gunicorn` olmalı
   - Build Command: `pip install -r requirements.txt`
   - Start Command:
     ```bash
     gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
     ```
2) Ortam değişkenleri (opsiyonel)
   - `BUILTWITH_API_KEY`: BuiltWith API erişimi için
3) Doğrulama
   - `GET /health` 200 dönmeli
   - Arayüz: kök `/` açılmalı, “Analyze” butonu `/analyze`’ı çalıştırmalı


### 5) Yapı ve Modüller
```
app.py                    # Flask giriş noktası (/, /health, /analyze, /simulate)
core/
  orchestrator.py         # run_simulation + geniş iş akışı (analyze_workflow)
  mx_analyzer.py          # MX analizi ve test-dostu fetch_mx_records wrapper’ı
  builtwith_client.py     # BuiltWith alma + test-dostu fetch_technology_stack
  holehe_runner.py        # Holehe entegrasyonu + enumerate_accounts wrapper’ı
  smtp_probe.py           # SMTP RCPT probing (opsiyonel)
utils/
  helpers.py, validators.py
templates/
  base.html, index.html, result.html
tests/
  test_simulation.py        # Unit testler (monkeypatch ile)
  test_integrations_live.py # Env ile açılan canlı entegrasyon testleri
```


### 6) Sık Karşılaşılan Sorunlar
- 502 (Render): Çoğunlukla `gunicorn` yok veya yanlış Start Command. Çözüm:
  - `requirements.txt` → `gunicorn>=21.2`
  - Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- 404 kök `/`: `app.py` içinde kök rota yok. Çözüm: `@app.get("/", endpoint="index")` ile `index.html` render edin.
- TemplateNotFound: `templates/result.html` eksik. Basit bir `result.html` ekleyin.
- BuildError url_for('index'): Kök endpoint adı `index` değilse bu olur. Çözüm: `@app.get("/", endpoint="index")` ya da fonksiyon adını `index` yapın.
- NotImplementedError (test): Üretim kodunda wrapper’ları sağlayın veya testte monkeypatch edin.
- SMTP çalışmıyor: Birçok sağlayıcı outbound 25/TCP’yi kısıtlar. Alternatif SMTP relay veya özel ağ gerekir.


### 7) Geliştirme İpuçları
- Hot reload: `flask run --debug`
- Prod benzeri lokal: `gunicorn --reload app:app --bind 0.0.0.0:8000`
- Yeni bağımlılık: `python -m pip install <paket>` ardından `git add requirements.txt` (sabit sürüm eklemek isterseniz pin’leyin)


### 8) Örnek İstekler
```bash
# Health
curl https://<host>/health

# Simülasyon (JSON)
curl -X POST https://<host>/simulate \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Ada","last_name":"Lovelace","domain":"example.com","use_builtwith":true}'

# Form tabanlı (JSON görüntüleme)
curl "https://<host>/analyze?domain=example.com&format=json"
```


### 9) Güvenlik ve Etik
Bu araç yalnızca eğitim, keşif ve meşru denetim amaçlarıyla sağlanır. Kendi olmayan etki alanları üzerinde çalıştırmadan önce yetki alınız.
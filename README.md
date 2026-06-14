# APEX Financial Intelligence Platform

APEX Financial Intelligence Platform adalah sistem trading dan analisis pasar generasi berikutnya yang menggabungkan **Multi-Agent AI**, **Digital Twin Simulation**, **Sentiment Engine**, dan **CISO Command Center** dalam satu arsitektur terpadu. Platform ini dirancang untuk institusi finansial kuantitatif yang membutuhkan kecepatan, akurasi, dan keamanan operasional tingkat tinggi.

## Arsitektur Sistem

- **Backend (FastAPI + SQLAlchemy)**: Modular monolith dengan pattern Repository dan Service layer.
- **Frontend (React + Vite + Tailwind)**: Dashboard trading, portfolio, dan intelligence center.
- **Telegram Bot (aiogram)**: Integrasi notifikasi real-time dan kontrol operasional.
- **CISO Dashboard (Streamlit)**: Command center read-only untuk monitoring operasional, sinyal AI, dan audit keamanan.
- **Multi-Agent System**: Koordinator agen AI (Market, Risk, Sentiment) yang berdiskusi paralel sebelum menghasilkan konsensus.
- **Digital Twin Engine**: Simulasi skenarioAlternatif (Aggressive, Moderate, Conservative) untuk validasi strategi.
- **Sentiment Engine (Ollama)**: Analisis sentimen berita mata uang kripto menggunakan model lokal.
- **Market Collector (CCXT + APScheduler)**: Backfill dan pengambilan data historis + realtime dari Binance.
- **Execution Engine**: Dukungan Paper Trading dan Live Trading toggle via `.env`.
- **Security Middleware**: Rate limiting (`slowapi`), CORS strict, AES encryption untuk API key.

## Prasyarat Sistem

- Docker & Docker Compose
- Python 3.12
- Node.js 22+
- Ollama (untuk Sentiment Engine lokal)
- PostgreSQL 16 & Redis 7 (via Docker)

## Instalasi Lokal

Salin `.env.example` menjadi `.env` pada root, lalu atur variabel yang dibutuhkan (khususnya `JWT_SECRET_KEY`, `ENCRYPTION_KEY`, `BACKEND_CORS_ORIGINS`).

Jalankan perintah berikut:

```bash
make prod-build
make prod-up
make logs
```

Untuk backup database:

```bash
make backup
```

Untuk mematikan sistem:

```bash
make prod-down
```

## Struktur Direktori Utama

```
backend/
  app/
    api/
    core/
    database/
    integrations/
    schemas/
    services/
    tasks/
  models/
frontend/
telegram-bot/
ciso-dashboard/
infrastructure/
docker/
scripts/
backups/
```

## Peringatan Keamanan

- **Jangan pernah commit file `.env` ke repository.**
- **Jangan commit model AI `.joblib`** (`backend/models/*.joblib`) karena ukuran file besar dan berisi aset proprietary.
- **Folder `backups/`** berisi dump database dan harus diabaikan oleh Git.
- Pastikan `ENCRYPTION_KEY` memiliki nilai Fernet base64 yang valid sebelum menjalankan aplikasi di production.

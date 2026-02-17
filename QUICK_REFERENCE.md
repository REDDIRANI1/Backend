# Quick Reference Card 🚀

## 🏃 Quick Start

### Using Docker
```bash
docker-compose up --build
```

### Without Docker (Windows)
```powershell
# Terminal 1: FastAPI
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: Celery Worker
.\venv\Scripts\Activate.ps1
celery -A app.celery_app worker --loglevel=info --pool=solo
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/v1/webhooks/transactions` | Receive webhook |
| GET | `/v1/transactions/{id}` | Get transaction status |

---

## 🧪 Quick Test

```bash
# 1. Health check
curl http://localhost:8000/

# 2. Send webhook
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_test_001",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR"
  }'

# 3. Check status (immediately)
curl http://localhost:8000/v1/transactions/txn_test_001
# Status: PROCESSING

# 4. Wait 35 seconds, check again
sleep 35
curl http://localhost:8000/v1/transactions/txn_test_001
# Status: PROCESSED
```

---

## 📦 Project Structure

```
Backend/
├── app/
│   ├── main.py          # FastAPI app
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── tasks.py         # Celery tasks
│   ├── database.py      # DB connection
│   ├── config.py        # Settings
│   └── celery_app.py    # Celery config
├── docker-compose.yml   # Docker setup
├── requirements.txt     # Dependencies
├── test_webhook.py      # Test suite
└── README.md           # Documentation
```

---

## 🔧 Common Commands

### Docker
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up --build
```

### Database
```bash
# Connect to PostgreSQL
docker exec -it webhook_postgres psql -U webhook_user -d webhook_db

# View transactions
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;

# Count by status
SELECT status, COUNT(*) FROM transactions GROUP BY status;
```

### Celery
```bash
# Check active tasks
celery -A app.celery_app inspect active

# Purge queue
celery -A app.celery_app purge
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change `APP_PORT` in `.env` |
| Database connection failed | Check PostgreSQL is running |
| Celery not processing | Verify Redis is accessible |
| Import errors | Activate venv: `.\venv\Scripts\Activate.ps1` |

---

## 📊 Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 202 | Accepted (webhook received) |
| 404 | Transaction not found |
| 500 | Server error |

---

## 🔐 Environment Variables

```env
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## 🌐 Deployment

**Easiest**: Railway
1. Push to GitHub
2. Connect to Railway
3. Add PostgreSQL + Redis
4. Deploy!

**See**: `DEPLOYMENT.md` for detailed guides

---

## 📚 Documentation

- **Full API Docs**: `API_DOCUMENTATION.md`
- **Windows Setup**: `WINDOWS_SETUP.md`
- **Deployment**: `DEPLOYMENT.md`
- **Interactive Docs**: `http://localhost:8000/docs`

---

## ✅ Success Criteria

- [x] Webhook responds < 500ms
- [x] Background processing with 30s delay
- [x] Idempotency (duplicate handling)
- [x] Persistent storage (PostgreSQL)
- [x] Status tracking
- [x] Error handling & retries

---

## 🎯 Next Steps

1. ✅ Test locally: `python test_webhook.py`
2. 🚀 Deploy to cloud (Railway recommended)
3. 📊 Add monitoring (Sentry)
4. 🔐 Add authentication
5. 📈 Scale as needed

---

**Need help?** Check README.md or open an issue!

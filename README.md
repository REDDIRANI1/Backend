# Transaction Webhook Service 🚀

A production-ready FastAPI service that receives transaction webhooks from external payment processors (like RazorPay), acknowledges them immediately, and processes them reliably in the background.

## 🌟 Features

- **Fast Response**: Returns `202 Accepted` within 500ms
- **Background Processing**: Processes transactions asynchronously with Celery
- **Idempotency**: Handles duplicate webhooks gracefully
- **Persistent Storage**: Uses PostgreSQL for reliable data storage
- **Production Ready**: Includes Docker setup, error handling, and logging
- **RESTful API**: Clean, well-documented endpoints

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│  (Webhook)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌───────────────────────────────┐  │
│  │  POST /v1/webhooks/transactions│  │
│  │  Returns 202 Accepted (<500ms) │  │
│  └───────────────┬─────────────────┘  │
└──────────────────┼─────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  PostgreSQL DB  │
         │  (Store txn)    │
         └─────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Celery Queue   │
         │   (via Redis)   │
         └─────────┬───────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Celery Worker   │
         │ (30s delay +    │
         │  processing)    │
         └─────────┬───────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Update Status  │
         │   PROCESSED     │
         └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   cd Backend
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Redis (port 6379)
   - FastAPI application (port 8000)
   - Celery worker

3. **Verify the service is running**
   ```bash
   curl http://localhost:8000/
   ```

   Expected response:
   ```json
   {
     "status": "HEALTHY",
     "current_time": "2024-01-15T10:30:00Z"
   }
   ```

### Option 2: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL and Redis**
   ```bash
   # Using Docker
   docker run -d -p 5432:5432 -e POSTGRES_USER=webhook_user -e POSTGRES_PASSWORD=webhook_password -e POSTGRES_DB=webhook_db postgres:15-alpine
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Start the FastAPI application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Start the Celery worker** (in a new terminal)
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

## 📡 API Endpoints

### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "HEALTHY",
  "current_time": "2024-01-15T10:30:00Z"
}
```

### 2. Webhook Endpoint
```http
POST /v1/webhooks/transactions
Content-Type: application/json

{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500,
  "currency": "INR"
}
```

**Response (202 Accepted):**
```json
{
  "message": "Webhook received",
  "transaction_id": "txn_abc123def456"
}
```

### 3. Query Transaction Status
```http
GET /v1/transactions/{transaction_id}
```

**Response:**
```json
[{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500,
  "currency": "INR",
  "status": "PROCESSED",
  "created_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:30:30Z"
}]
```

## 🧪 Testing

### Automated Test Suite

Run the comprehensive test script:

```bash
python test_webhook.py
```

This tests:
- ✅ Health check endpoint
- ✅ Single transaction processing
- ✅ Duplicate transaction handling (idempotency)
- ✅ Response time (<500ms)
- ✅ Background processing (30s delay)
- ✅ Transaction status retrieval

### Manual Testing

1. **Send a webhook:**
   ```bash
   curl -X POST http://localhost:8000/v1/webhooks/transactions \
     -H "Content-Type: application/json" \
     -d '{
       "transaction_id": "txn_test_001",
       "source_account": "acc_user_789",
       "destination_account": "acc_merchant_456",
       "amount": 1500,
       "currency": "INR"
     }'
   ```

2. **Check status immediately:**
   ```bash
   curl http://localhost:8000/v1/transactions/txn_test_001
   ```
   Status should be `PROCESSING`

3. **Wait 30+ seconds and check again:**
   ```bash
   curl http://localhost:8000/v1/transactions/txn_test_001
   ```
   Status should be `PROCESSED`

4. **Test idempotency (send same webhook multiple times):**
   ```bash
   # Send the same request 3 times
   for i in {1..3}; do
     curl -X POST http://localhost:8000/v1/webhooks/transactions \
       -H "Content-Type: application/json" \
       -d '{
         "transaction_id": "txn_test_001",
         "source_account": "acc_user_789",
         "destination_account": "acc_merchant_456",
         "amount": 1500,
         "currency": "INR"
       }'
   done
   ```
   Only one transaction should be created in the database.

## 🔧 Technical Choices

### Why FastAPI?
- **Performance**: Async support and high performance
- **Type Safety**: Pydantic models for validation
- **Documentation**: Auto-generated OpenAPI docs at `/docs`
- **Modern**: Built on Python 3.11+ with type hints

### Why Celery + Redis?
- **Reliability**: Proven task queue for background processing
- **Scalability**: Easy to add more workers
- **Monitoring**: Built-in monitoring and retry mechanisms
- **Flexibility**: Can handle complex workflows

### Why PostgreSQL?
- **ACID Compliance**: Ensures data consistency
- **Performance**: Excellent for transactional workloads
- **Reliability**: Battle-tested in production
- **Features**: Rich indexing and query capabilities

### Key Design Decisions

1. **Idempotency via Primary Key**: Using `transaction_id` as the primary key ensures natural idempotency at the database level.

2. **Immediate Response**: The webhook endpoint commits the transaction to the database and triggers the background task before responding, ensuring sub-500ms response times.

3. **Status Tracking**: Three states (`PROCESSING`, `PROCESSED`, `FAILED`) provide clear visibility into transaction lifecycle.

4. **Error Handling**: Celery tasks include retry logic with exponential backoff for transient failures.

5. **Database Indexes**: Added indexes on `status` and `created_at` for efficient querying.

## 📊 Monitoring

### Check Celery Worker Status
```bash
celery -A app.celery_app inspect active
```

### View Logs
```bash
# FastAPI logs
docker-compose logs -f web

# Celery logs
docker-compose logs -f celery_worker

# Database logs
docker-compose logs -f postgres
```

### Database Queries
```bash
# Connect to PostgreSQL
docker exec -it webhook_postgres psql -U webhook_user -d webhook_db

# View all transactions
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;

# Count by status
SELECT status, COUNT(*) FROM transactions GROUP BY status;
```

## 🌐 Deployment

### Deploy to Cloud (Example: Railway/Render)

1. **Set environment variables:**
   ```
   DATABASE_URL=<your-postgres-url>
   REDIS_URL=<your-redis-url>
   ```

2. **Deploy the application:**
   - Push to GitHub
   - Connect to Railway/Render
   - Deploy both web service and worker

3. **Scale workers as needed:**
   ```bash
   # Railway CLI example
   railway scale celery_worker --replicas 3
   ```

### Production Checklist
- [ ] Set strong database passwords
- [ ] Enable SSL for database connections
- [ ] Configure CORS if needed
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Configure log aggregation
- [ ] Set up alerts for failed tasks
- [ ] Enable database backups
- [ ] Configure rate limiting

## 📁 Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── celery_app.py        # Celery configuration
│   └── tasks.py             # Background tasks
├── docker-compose.yml       # Docker services
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── test_webhook.py         # Test suite
├── .env.example           # Environment template
├── .gitignore
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Issue: "Connection refused" to PostgreSQL
**Solution**: Ensure PostgreSQL is running and the connection string is correct.

### Issue: Celery tasks not processing
**Solution**: Check that the Celery worker is running and Redis is accessible.

### Issue: Response time > 500ms
**Solution**: Check database connection pool settings and ensure indexes are created.

### Issue: Duplicate transactions being processed
**Solution**: Verify that `transaction_id` is the primary key in the database.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, PostgreSQL, and Celery

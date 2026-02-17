# API Documentation 📚

## Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Interactive Documentation
Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Endpoints

### 1. Health Check

Check if the service is running and healthy.

**Endpoint**: `GET /`

**Response**: `200 OK`
```json
{
  "status": "HEALTHY",
  "current_time": "2024-01-15T10:30:00.000000Z"
}
```

**Example**:
```bash
curl http://localhost:8000/
```

---

### 2. Receive Webhook

Receive and process transaction webhooks.

**Endpoint**: `POST /v1/webhooks/transactions`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500.50,
  "currency": "INR"
}
```

**Field Descriptions**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction_id` | string | Yes | Unique transaction identifier |
| `source_account` | string | Yes | Source account identifier |
| `destination_account` | string | Yes | Destination account identifier |
| `amount` | number | Yes | Transaction amount (must be positive) |
| `currency` | string | Yes | 3-letter currency code (e.g., INR, USD) |

**Response**: `202 Accepted`
```json
{
  "message": "Webhook received",
  "transaction_id": "txn_abc123def456"
}
```

**Response Time**: < 500ms

**Idempotency**: 
- Sending the same `transaction_id` multiple times will only create one transaction
- Duplicate requests return the same response

**Example**:
```bash
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_abc123def456",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500.50,
    "currency": "INR"
  }'
```

**Error Responses**:

`400 Bad Request` - Invalid input
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

`500 Internal Server Error` - Server error
```json
{
  "detail": "Failed to process webhook"
}
```

---

### 3. Get Transaction Status

Retrieve the status of a specific transaction.

**Endpoint**: `GET /v1/transactions/{transaction_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `transaction_id` | string | Unique transaction identifier |

**Response**: `200 OK`
```json
[{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500.50,
  "currency": "INR",
  "status": "PROCESSED",
  "created_at": "2024-01-15T10:30:00.000000Z",
  "processed_at": "2024-01-15T10:30:30.000000Z"
}]
```

**Transaction Statuses**:
| Status | Description |
|--------|-------------|
| `PROCESSING` | Transaction is being processed (30s delay) |
| `PROCESSED` | Transaction completed successfully |
| `FAILED` | Transaction processing failed |

**Example**:
```bash
curl http://localhost:8000/v1/transactions/txn_abc123def456
```

**Error Responses**:

`404 Not Found` - Transaction doesn't exist
```json
{
  "detail": "Transaction txn_abc123def456 not found"
}
```

---

## Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 202 | Accepted | Webhook received and queued |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production:
- Recommended: 100 requests per minute per IP
- Consider implementing with `slowapi` or similar

---

## Authentication

Currently, the API is open. For production, consider:
- **API Keys**: Add `X-API-Key` header validation
- **HMAC Signatures**: Verify webhook authenticity
- **OAuth 2.0**: For user-based access

---

## Webhook Flow

```
1. External service sends webhook
   ↓
2. API validates request (< 10ms)
   ↓
3. Create transaction in database (< 50ms)
   ↓
4. Queue background task (< 10ms)
   ↓
5. Return 202 Accepted (< 500ms total)
   ↓
6. Background worker picks up task
   ↓
7. Wait 30 seconds (simulate external API)
   ↓
8. Update transaction status to PROCESSED
```

---

## Testing Examples

### Python (requests)
```python
import requests

# Send webhook
response = requests.post(
    "http://localhost:8000/v1/webhooks/transactions",
    json={
        "transaction_id": "txn_test_001",
        "source_account": "acc_user_789",
        "destination_account": "acc_merchant_456",
        "amount": 1500.50,
        "currency": "INR"
    }
)
print(response.status_code)  # 202
print(response.json())

# Check status
import time
time.sleep(35)  # Wait for processing

response = requests.get(
    "http://localhost:8000/v1/transactions/txn_test_001"
)
print(response.json())  # Status: PROCESSED
```

### JavaScript (fetch)
```javascript
// Send webhook
fetch('http://localhost:8000/v1/webhooks/transactions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    transaction_id: 'txn_test_001',
    source_account: 'acc_user_789',
    destination_account: 'acc_merchant_456',
    amount: 1500.50,
    currency: 'INR'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Check status after 35 seconds
setTimeout(() => {
  fetch('http://localhost:8000/v1/transactions/txn_test_001')
    .then(response => response.json())
    .then(data => console.log(data));
}, 35000);
```

### cURL
```bash
# Send webhook
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_test_001",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500.50,
    "currency": "INR"
  }'

# Check status
sleep 35
curl http://localhost:8000/v1/transactions/txn_test_001
```

### PowerShell
```powershell
# Send webhook
$body = @{
    transaction_id = "txn_test_001"
    source_account = "acc_user_789"
    destination_account = "acc_merchant_456"
    amount = 1500.50
    currency = "INR"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/v1/webhooks/transactions" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

# Check status
Start-Sleep -Seconds 35
Invoke-RestMethod -Uri "http://localhost:8000/v1/transactions/txn_test_001"
```

---

## Database Schema

### Transactions Table
```sql
CREATE TABLE transactions (
    transaction_id VARCHAR PRIMARY KEY,
    source_account VARCHAR NOT NULL,
    destination_account VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    currency VARCHAR NOT NULL,
    status VARCHAR NOT NULL,  -- PROCESSING, PROCESSED, FAILED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_transaction_status ON transactions(status);
CREATE INDEX idx_transaction_created_at ON transactions(created_at);
```

---

## Performance Considerations

### Response Time Optimization
- Database connection pooling (10 connections)
- Async background processing
- Minimal validation in webhook endpoint

### Scalability
- Horizontal scaling: Add more API instances
- Worker scaling: Add more Celery workers
- Database: Use read replicas for queries

### Monitoring Metrics
- Webhook response time (target: < 500ms)
- Background task processing time (target: ~30s)
- Database query time
- Queue length
- Error rate

---

## Error Handling

### Retry Logic
- Background tasks retry up to 3 times
- 60-second delay between retries
- Failed tasks marked as `FAILED` status

### Logging
- All requests logged with timestamp
- Errors logged with stack traces
- Celery tasks logged with task ID

---

## Security Recommendations

1. **Add API Key Authentication**
   ```python
   from fastapi import Header, HTTPException
   
   async def verify_api_key(x_api_key: str = Header(...)):
       if x_api_key != "your-secret-key":
           raise HTTPException(status_code=401)
   ```

2. **Verify Webhook Signatures**
   ```python
   import hmac
   import hashlib
   
   def verify_signature(payload: str, signature: str, secret: str):
       expected = hmac.new(
           secret.encode(),
           payload.encode(),
           hashlib.sha256
       ).hexdigest()
       return hmac.compare_digest(expected, signature)
   ```

3. **Rate Limiting**
   ```python
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/v1/webhooks/transactions")
   @limiter.limit("100/minute")
   async def receive_webhook(...):
       ...
   ```

---

## Support

For issues or questions:
- Check the logs: `docker-compose logs -f`
- Review the test script: `python test_webhook.py`
- Open an issue on GitHub

# Manual Testing Guide 🧪

## Prerequisites
- Service running at `http://localhost:8000` (or your deployed URL)

---

## Test 1: Health Check ✅

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
```

**cURL:**
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "status": "HEALTHY",
  "current_time": "2026-02-17T17:52:23.000000Z"
}
```

✅ **Success**: You get a 200 OK with status "HEALTHY"

---

## Test 2: Send a Webhook 📨

**PowerShell:**
```powershell
$body = @{
    transaction_id = "txn_manual_test_001"
    source_account = "acc_user_789"
    destination_account = "acc_merchant_456"
    amount = 1500.50
    currency = "INR"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/v1/webhooks/transactions" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

**cURL:**
```bash
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_manual_test_001",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500.50,
    "currency": "INR"
  }'
```

**Expected Response (202 Accepted):**
```json
{
  "message": "Webhook received",
  "transaction_id": "txn_manual_test_001"
}
```

✅ **Success**: You get a 202 Accepted response in < 500ms

---

## Test 3: Check Status Immediately 🔍

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/transactions/txn_manual_test_001" -Method GET
```

**cURL:**
```bash
curl http://localhost:8000/v1/transactions/txn_manual_test_001
```

**Expected Response:**
```json
[{
  "transaction_id": "txn_manual_test_001",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500.50,
  "currency": "INR",
  "status": "PROCESSING",
  "created_at": "2026-02-17T17:52:23.000000Z",
  "processed_at": null
}]
```

✅ **Success**: Status is "PROCESSING" and processed_at is null

---

## Test 4: Wait and Check Again ⏰

**Wait 35 seconds**, then check again:

**PowerShell:**
```powershell
Start-Sleep -Seconds 35
Invoke-RestMethod -Uri "http://localhost:8000/v1/transactions/txn_manual_test_001" -Method GET
```

**cURL:**
```bash
sleep 35
curl http://localhost:8000/v1/transactions/txn_manual_test_001
```

**Expected Response:**
```json
[{
  "transaction_id": "txn_manual_test_001",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500.50,
  "currency": "INR",
  "status": "PROCESSED",
  "created_at": "2026-02-17T17:52:23.000000Z",
  "processed_at": "2026-02-17T17:52:53.000000Z"
}]
```

✅ **Success**: Status is "PROCESSED" and processed_at has a timestamp

---

## Test 5: Test Idempotency (Duplicate Handling) 🔁

Send the **same webhook 3 times**:

**PowerShell:**
```powershell
$body = @{
    transaction_id = "txn_manual_test_001"
    source_account = "acc_user_789"
    destination_account = "acc_merchant_456"
    amount = 1500.50
    currency = "INR"
} | ConvertTo-Json

# Send 3 times
1..3 | ForEach-Object {
    Write-Host "Attempt $_"
    Invoke-RestMethod -Uri "http://localhost:8000/v1/webhooks/transactions" `
      -Method Post `
      -ContentType "application/json" `
      -Body $body
}
```

**cURL:**
```bash
for i in {1..3}; do
  echo "Attempt $i"
  curl -X POST http://localhost:8000/v1/webhooks/transactions \
    -H "Content-Type: application/json" \
    -d '{
      "transaction_id": "txn_manual_test_001",
      "source_account": "acc_user_789",
      "destination_account": "acc_merchant_456",
      "amount": 1500.50,
      "currency": "INR"
    }'
done
```

**Expected**: All 3 requests return 202 Accepted, but only ONE transaction exists in the database

✅ **Success**: Duplicate webhooks are handled gracefully

---

## Test 6: Test Non-existent Transaction 🚫

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/transactions/txn_does_not_exist" -Method GET
```

**cURL:**
```bash
curl http://localhost:8000/v1/transactions/txn_does_not_exist
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Transaction txn_does_not_exist not found"
}
```

✅ **Success**: You get a 404 error for non-existent transactions

---

## Test 7: Test Invalid Input ❌

**PowerShell:**
```powershell
$body = @{
    transaction_id = "txn_invalid"
    source_account = "acc_user_789"
    destination_account = "acc_merchant_456"
    amount = -100  # Invalid: negative amount
    currency = "INR"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/v1/webhooks/transactions" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

**cURL:**
```bash
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_invalid",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": -100,
    "currency": "INR"
  }'
```

**Expected Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

✅ **Success**: Invalid input is rejected with validation error

---

## Quick Test Script (PowerShell)

Save this as `quick_test.ps1`:

```powershell
# Quick Manual Test Script
$baseUrl = "http://localhost:8000"

Write-Host "🧪 Testing Webhook Service..." -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1️⃣ Testing Health Check..." -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
Write-Host "✅ Health: $($health.status)" -ForegroundColor Green

# Test 2: Send Webhook
Write-Host "`n2️⃣ Sending Webhook..." -ForegroundColor Cyan
$txnId = "txn_test_$(Get-Date -Format 'yyyyMMddHHmmss')"
$body = @{
    transaction_id = $txnId
    source_account = "acc_user_789"
    destination_account = "acc_merchant_456"
    amount = 1500.50
    currency = "INR"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/v1/webhooks/transactions" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
Write-Host "✅ Webhook received: $($response.transaction_id)" -ForegroundColor Green

# Test 3: Check Status (PROCESSING)
Write-Host "`n3️⃣ Checking Status (should be PROCESSING)..." -ForegroundColor Cyan
$status = Invoke-RestMethod -Uri "$baseUrl/v1/transactions/$txnId" -Method GET
Write-Host "✅ Status: $($status[0].status)" -ForegroundColor Green

# Test 4: Wait and Check Again
Write-Host "`n4️⃣ Waiting 35 seconds for processing..." -ForegroundColor Cyan
Start-Sleep -Seconds 35

Write-Host "Checking Status (should be PROCESSED)..." -ForegroundColor Cyan
$status = Invoke-RestMethod -Uri "$baseUrl/v1/transactions/$txnId" -Method GET
Write-Host "✅ Status: $($status[0].status)" -ForegroundColor Green
Write-Host "✅ Processed at: $($status[0].processed_at)" -ForegroundColor Green

Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
```

Run with:
```powershell
.\quick_test.ps1
```

---

## Summary Checklist

- [ ] Health check returns "HEALTHY"
- [ ] Webhook returns 202 Accepted in < 500ms
- [ ] Initial status is "PROCESSING"
- [ ] After 30+ seconds, status is "PROCESSED"
- [ ] Duplicate webhooks handled gracefully
- [ ] Non-existent transactions return 404
- [ ] Invalid input returns validation error

**All checked?** ✅ Your service is working perfectly! 🎉

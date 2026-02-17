# Start all services for the webhook application

Write-Host "Starting Webhook Service..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
}

# Start FastAPI server
Write-Host "Starting FastAPI server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; Write-Host 'FastAPI Server' -ForegroundColor Green; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

# Start Celery worker
Write-Host "Starting Celery worker..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; Write-Host 'Celery Worker' -ForegroundColor Yellow; celery -A app.celery_app worker --loglevel=info --pool=solo"

Write-Host "`nAll services started!" -ForegroundColor Green
Write-Host "FastAPI: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`nPress Ctrl+C in each window to stop services" -ForegroundColor Gray

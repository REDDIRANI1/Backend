# Windows Setup Guide (Without Docker)

This guide will help you set up the webhook service on Windows without Docker.

## Prerequisites

1. **Python 3.11+** ✅ (Already installed)
2. **PostgreSQL** - Download from https://www.postgresql.org/download/windows/
3. **Redis** - Use WSL2 or download from https://github.com/microsoftarchive/redis/releases

## Step-by-Step Setup

### 1. Install PostgreSQL

1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run the installer and follow the wizard
3. Remember the password you set for the `postgres` user
4. Default port: 5432

After installation, create the database:

```powershell
# Open PowerShell as Administrator
# Navigate to PostgreSQL bin directory (adjust version as needed)
cd "C:\Program Files\PostgreSQL\15\bin"

# Create user and database
.\psql -U postgres
```

In the PostgreSQL prompt:
```sql
CREATE USER webhook_user WITH PASSWORD 'webhook_password';
CREATE DATABASE webhook_db OWNER webhook_user;
GRANT ALL PRIVILEGES ON DATABASE webhook_db TO webhook_user;
\q
```

### 2. Install Redis

**Option A: Using WSL2 (Recommended)**

```powershell
# Install WSL2 if not already installed
wsl --install

# In WSL terminal
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Option B: Using Windows Port**

1. Download Redis for Windows: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`

**Option C: Use a Cloud Redis (Easiest)**

- Sign up for a free Redis instance at https://redis.com/try-free/
- Or use Upstash: https://upstash.com/

### 3. Install Python Dependencies

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

Update the `.env` file with your actual credentials:

```env
DATABASE_URL=postgresql://webhook_user:webhook_password@localhost:5432/webhook_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 5. Run the Application

You need to run THREE separate terminals:

**Terminal 1: FastAPI Application**
```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Celery Worker**
```powershell
.\venv\Scripts\Activate.ps1
celery -A app.celery_app worker --loglevel=info --pool=solo
```
Note: Use `--pool=solo` on Windows as it doesn't support the default pool.

**Terminal 3: Redis Server** (if running locally)
```powershell
# If using WSL
wsl sudo service redis-server start

# If using Windows Redis
cd path\to\redis
.\redis-server.exe
```

### 6. Verify Installation

Open a new terminal and test:

```powershell
# Test health check
curl http://localhost:8000/

# Or use PowerShell
Invoke-WebRequest -Uri http://localhost:8000/ -Method GET
```

### 7. Run Tests

```powershell
.\venv\Scripts\Activate.ps1
python test_webhook.py
```

## Alternative: Using Docker Desktop

If you prefer Docker:

1. Install Docker Desktop for Windows: https://www.docker.com/products/docker-desktop/
2. Enable WSL2 backend
3. Run: `docker-compose up --build`

## Troubleshooting

### Issue: PostgreSQL connection refused
- Check if PostgreSQL service is running: Services → postgresql-x64-15
- Verify connection string in `.env`

### Issue: Redis connection refused
- Check if Redis is running
- For WSL: `wsl sudo service redis-server status`

### Issue: Celery worker not starting
- Use `--pool=solo` flag on Windows
- Ensure Redis is accessible

### Issue: Import errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## Quick Start Script

Save this as `start.ps1`:

```powershell
# Start all services
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; celery -A app.celery_app worker --loglevel=info --pool=solo"
```

Run: `.\start.ps1`

## Next Steps

1. Test the API endpoints (see README.md)
2. Deploy to cloud (Railway, Render, etc.)
3. Set up monitoring and logging

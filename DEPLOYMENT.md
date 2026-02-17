# Cloud Deployment Guide 🚀

This guide covers deploying the webhook service to various cloud platforms.

## Option 1: Railway (Recommended - Easiest)

Railway provides PostgreSQL, Redis, and easy deployment.

### Steps:

1. **Create Railway Account**
   - Go to https://railway.app/
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Add PostgreSQL**
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway will create a database and provide connection URL

4. **Add Redis**
   - Click "+ New"
   - Select "Database" → "Redis"
   - Railway will create Redis instance

5. **Configure Web Service**
   - Select your app service
   - Add environment variables:
     ```
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     REDIS_URL=${{Redis.REDIS_URL}}
     CELERY_BROKER_URL=${{Redis.REDIS_URL}}
     CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
     ```
   - Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. **Add Celery Worker Service**
   - Click "+ New" → "Empty Service"
   - Connect same GitHub repo
   - Set start command: `celery -A app.celery_app worker --loglevel=info`
   - Add same environment variables

7. **Deploy**
   - Railway will automatically deploy
   - Get your public URL from the web service

### Cost: 
- Free tier: $5 credit/month
- Paid: ~$10-20/month

---

## Option 2: Render

### Steps:

1. **Create Render Account**
   - Go to https://render.com/
   - Sign up with GitHub

2. **Create PostgreSQL Database**
   - Dashboard → "New" → "PostgreSQL"
   - Choose free tier
   - Note the Internal Database URL

3. **Create Redis Instance**
   - Dashboard → "New" → "Redis"
   - Choose free tier
   - Note the Internal Redis URL

4. **Create Web Service**
   - Dashboard → "New" → "Web Service"
   - Connect GitHub repository
   - Settings:
     - **Name**: webhook-api
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     DATABASE_URL=<your-postgres-internal-url>
     REDIS_URL=<your-redis-internal-url>
     CELERY_BROKER_URL=<your-redis-internal-url>
     CELERY_RESULT_BACKEND=<your-redis-internal-url>
     ```

5. **Create Background Worker**
   - Dashboard → "New" → "Background Worker"
   - Connect same repository
   - Settings:
     - **Name**: webhook-worker
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `celery -A app.celery_app worker --loglevel=info`
   - Add same environment variables

6. **Deploy**
   - Render will build and deploy automatically
   - Your API will be at: `https://webhook-api.onrender.com`

### Cost:
- Free tier available (services sleep after inactivity)
- Paid: $7/month per service

---

## Option 3: Heroku

### Steps:

1. **Install Heroku CLI**
   ```bash
   # Windows
   winget install Heroku.HerokuCLI
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   cd Backend
   heroku create webhook-service-api
   ```

4. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Add Redis**
   ```bash
   heroku addons:create heroku-redis:mini
   ```

6. **Create Procfile**
   ```bash
   echo "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT" > Procfile
   echo "worker: celery -A app.celery_app worker --loglevel=info" >> Procfile
   ```

7. **Deploy**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

8. **Scale Worker**
   ```bash
   heroku ps:scale worker=1
   ```

9. **View Logs**
   ```bash
   heroku logs --tail
   ```

### Cost:
- Mini PostgreSQL: $5/month
- Mini Redis: $3/month
- Dyno: $7/month
- Total: ~$15/month

---

## Option 4: DigitalOcean App Platform

### Steps:

1. **Create DigitalOcean Account**
   - Go to https://www.digitalocean.com/
   - Sign up and add payment method

2. **Create Managed PostgreSQL**
   - Databases → "Create Database"
   - Choose PostgreSQL
   - Select $15/month plan
   - Note connection details

3. **Create Managed Redis**
   - Databases → "Create Database"
   - Choose Redis
   - Select $15/month plan

4. **Create App**
   - Apps → "Create App"
   - Connect GitHub repository
   - Configure components:

   **Web Component:**
   - Name: webhook-api
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
   **Worker Component:**
   - Name: webhook-worker
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `celery -A app.celery_app worker --loglevel=info`

5. **Add Environment Variables**
   ```
   DATABASE_URL=<postgres-connection-string>
   REDIS_URL=<redis-connection-string>
   CELERY_BROKER_URL=<redis-connection-string>
   CELERY_RESULT_BACKEND=<redis-connection-string>
   ```

6. **Deploy**
   - DigitalOcean will build and deploy

### Cost:
- App Platform: $5/month
- PostgreSQL: $15/month
- Redis: $15/month
- Total: ~$35/month

---

## Option 5: AWS (Advanced)

For production-grade deployment with full control.

### Architecture:
- **ECS/Fargate**: Run containers
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed Redis
- **ALB**: Load balancer
- **CloudWatch**: Logging

### Quick Setup with CDK/Terraform:
This requires more setup. Consider using AWS Copilot or ECS CLI for easier deployment.

### Cost:
- Highly variable, ~$50-200/month depending on usage

---

## Option 6: Google Cloud Run (Serverless)

### Limitations:
- Cloud Run is stateless and may not be ideal for Celery workers
- Better suited for simpler async tasks

### Alternative:
Use **Cloud Tasks** instead of Celery for background processing.

---

## Recommended Setup for Production

### For Small Projects (< 1000 webhooks/day):
**Railway** or **Render Free Tier**
- Cost: $0-10/month
- Easy setup
- Auto-scaling

### For Medium Projects (1000-10000 webhooks/day):
**Render** or **Railway Paid**
- Cost: $20-50/month
- Better performance
- Monitoring included

### For Large Projects (> 10000 webhooks/day):
**DigitalOcean** or **AWS**
- Cost: $50-200/month
- Full control
- Advanced monitoring
- Auto-scaling

---

## Post-Deployment Checklist

- [ ] Test all endpoints
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Configure alerts
- [ ] Enable SSL/HTTPS
- [ ] Set up database backups
- [ ] Configure CORS if needed
- [ ] Add rate limiting
- [ ] Set up CI/CD pipeline
- [ ] Document API for external users
- [ ] Load testing

---

## Testing Your Deployed API

```bash
# Replace with your deployed URL
export API_URL="https://your-app.railway.app"

# Test health check
curl $API_URL/

# Send webhook
curl -X POST $API_URL/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_prod_001",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR"
  }'

# Check status
curl $API_URL/v1/transactions/txn_prod_001
```

---

## Monitoring

### Railway:
- Built-in metrics and logs
- Access via dashboard

### Render:
- Logs available in dashboard
- Add Sentry for error tracking

### Heroku:
```bash
heroku logs --tail
heroku ps
```

### General Monitoring Tools:
- **Sentry**: Error tracking
- **DataDog**: Full observability
- **New Relic**: APM
- **Uptime Robot**: Uptime monitoring

---

## Scaling Considerations

### Horizontal Scaling:
- Add more Celery workers
- Use load balancer for API

### Vertical Scaling:
- Increase dyno/instance size
- Upgrade database tier

### Database Optimization:
- Add indexes (already included)
- Use connection pooling
- Consider read replicas for high traffic

### Caching:
- Add Redis caching for frequently accessed data
- Use CDN for static assets

---

## Security Best Practices

1. **Use Environment Variables**: Never commit credentials
2. **Enable SSL**: Always use HTTPS
3. **Rate Limiting**: Prevent abuse
4. **Authentication**: Add API keys for webhooks
5. **Input Validation**: Already implemented with Pydantic
6. **Database Security**: Use strong passwords, restrict access
7. **Monitoring**: Set up alerts for suspicious activity

---

## Need Help?

- Railway Docs: https://docs.railway.app/
- Render Docs: https://render.com/docs
- Heroku Docs: https://devcenter.heroku.com/
- DigitalOcean Docs: https://docs.digitalocean.com/

---

**Recommendation**: Start with **Railway** for the easiest deployment experience!

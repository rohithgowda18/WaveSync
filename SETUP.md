# WaveSync Setup Guide

## ✅ Step-by-Step Setup

### 1. Prerequisites Check
- [ ] Python 3.8+ installed
- [ ] AWS account with Lambda access
- [ ] AWS credentials ready

### 2. Clone/Navigate to Project
```bash
cd WaveSync
```

### 3. Create Environment File
The `.env` file is already created with template values. **Update with your credentials:**

**FILE:** `.env`
```env
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=eu-north-1
AWS_LAMBDA_FUNCTION=wavesync-function
```

### 4. Run Quick Start Script

**For Windows:**
```bash
run.bat
```

**For Linux/macOS:**
```bash
bash run.sh
```

This will:
- Create virtual environment
- Install all dependencies from `requirements.txt`
- Display next steps

### 5. Manual Setup (Optional)
If you prefer manual setup:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Terminal 1: Start API Server
```bash
python src/wavesync/frontend/app.py
```

**Output should show:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Verify API is running:**
- Open browser: `http://127.0.0.1:8000/docs`
- You should see FastAPI interactive documentation

### Terminal 2: Start Dashboard (Keep Terminal 1 Running)
```bash
cd frontend
streamlit run dashboard.py
```

**Output should show:**
```
  You can now view your Streamlit app in your browser.
  
  URL: http://localhost:8501
```

---

## 📝 How to Use

### 1. Upload Services
Use the API to upload services:

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "services": ["auth-service", "payment-service", "notification-service"]
  }'
```

Or use a Postman/Insomnia request:
- **Method:** POST
- **URL:** `http://127.0.0.1:8000/upload`
- **Body:**
```json
{
  "services": ["service1", "service2", "service3"]
}
```

### 2. Start Migration
```bash
curl -X POST "http://127.0.0.1:8000/start"
```

### 3. Monitor in Dashboard
Watch the Streamlit dashboard at `http://localhost:8501` for real-time updates:
- Metrics update every 2 seconds
- Status changes: PENDING → RECTIFYING → DEPLOYING → SUCCESS/FAILED
- Activity feed shows events

### 4. Check API Status
```bash
curl "http://127.0.0.1:8000/services"
```

Returns:
```json
{
  "service1": {
    "status": "SUCCESS",
    "url": "https://aws/service1"
  },
  "service2": {
    "status": "DEPLOYING",
    "url": null
  }
}
```

---

## 📁 File Structure Explained

| File/Folder | Purpose |
|-------------|---------|
| `.env` | Environment variables & credentials |
| `requirements.txt` | Python package dependencies |
| `src/wavesync/deploy.py` | AWS Lambda deployment functions - **reads from `.env`** |
| `frontend/app.py` | FastAPI server - **reads from `.env`** |
| `frontend/dashboard.py` | Streamlit dashboard - **reads from `.env`** |
| `run.bat` / `run.sh` | Quick start scripts |

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dotenv'"
**Solution:**
```bash
pip install python-dotenv
```

### Issue: "ConnectionError: Cannot connect to API"
**Solution:**
- Ensure API is running in Terminal 1: `python src/wavesync/frontend/app.py`
- Check if port 8000 is already in use
- Verify firewall settings

### Issue: "AWS credentials not found"
**Solution:**
- Verify `.env` file exists in project root
- Check credentials are correct: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Ensure `.env` is loaded before running scripts

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Kill the process using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/macOS:
lsof -i :8000
```

---

## 🔐 Security Checklist

- [ ] `.env` file created with your credentials
- [ ] `.env` is in `.gitignore` (already configured)
- [ ] Never commit `.env` to version control
- [ ] Use strong AWS credentials
- [ ] Rotate credentials regularly
- [ ] Limit IAM permissions for Lambda access

---

## 📊 Expected Behavior

### Successful Deployment Flow:
1. Services uploaded → Status: PENDING
2. Migration started → Status: RECTIFYING
3. AWS Lambda invoked → Status: DEPLOYING
4. Health check passes → Status: SUCCESS
5. Dashboard shows ✅ (green) for completed services

### Failed Deployment Flow:
1. AWS error occurs → Status: FAILED
2. Health check fails → Status: FAILED
3. Dashboard shows ❌ (red) for failed services

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all environment variables in `.env`
3. Ensure all dependencies installed: `pip list`
4. Check API logs for error messages
5. Review AWS Lambda function logs in AWS Console

---

## ✨ Next Steps

- [ ] Update `.env` with real AWS credentials
- [ ] Run quick start script
- [ ] Start API server in one terminal
- [ ] Start dashboard in another terminal
- [ ] Upload services and begin migration
- [ ] Monitor progress in real-time dashboard

**You're all set! Happy migrating! 🚀**

# WaveSync Quick Reference

## 🚀 Getting Started (5 Minutes)

```bash
# 1. Update your credentials in .env
# Edit: .env
#   AWS_ACCESS_KEY_ID=your_key
#   AWS_SECRET_ACCESS_KEY=your_secret

# 2. Run quick start (one-time)
run.bat          # Windows
bash run.sh      # Linux/macOS

# 3. Terminal 1: Start API
python src/wavesync/frontend/app.py

# 4. Terminal 2: Start Dashboard
cd frontend
streamlit run dashboard.py
```

---

## 📱 URLs & Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| **API** | `http://127.0.0.1:8000` | Migration pipeline |
| **API Docs** | `http://127.0.0.1:8000/docs` | Interactive API documentation |
| **Dashboard** | `http://127.0.0.1:8501` | Real-time monitoring |

---

## 🔌 API Endpoints

### Upload Services
```bash
POST /upload
Content-Type: application/json

{
  "services": ["service1", "service2", "service3"]
}
```

### Start Migration
```bash
POST /start
```

### Get Service Status
```bash
GET /services
```

### Health Check
```bash
GET /health
```

---

## 📊 Example Workflows

### Workflow 1: Test Deployment
```bash
# Terminal 1
python src/wavesync/frontend/app.py

# Terminal 2
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{"services": ["auth", "payment", "user"]}'

# Start migration
curl -X POST "http://127.0.0.1:8000/start"

# Monitor status
while true; do
  curl "http://127.0.0.1:8000/services"
  sleep 2
done
```

### Workflow 2: View Dashboard
```bash
# Terminal 1
python src/wavesync/frontend/app.py

# Terminal 2
cd frontend && streamlit run dashboard.py

# Open Dashboard
# Browser: http://127.0.0.1:8501
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.env` | 🔐 Your AWS credentials (NEVER commit!) |
| `src/wavesync/deploy.py` | AWS Lambda deployment functions |
| `frontend/app.py` | FastAPI migration server |
| `frontend/dashboard.py` | Streamlit monitoring dashboard |
| `requirements.txt` | Python dependencies |

---

## 🔧 Configuration

All config via `.env`:
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=eu-north-1
AWS_LAMBDA_FUNCTION=wavesync-function
API_URL=http://127.0.0.1:8000
API_PORT=8000
API_HOST=127.0.0.1
```

---

## ⚡ Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS

# Check if API is running
curl http://127.0.0.1:8000/health

# Check service status
curl http://127.0.0.1:8000/services

# Kill process on port 8000 (if stuck)
netstat -ano | findstr :8000   # Windows (find PID)
taskkill /PID <PID> /F         # Windows (kill)
lsof -ti :8000 | xargs kill    # Linux/macOS
```

---

## 📊 Service Status Codes

| Status | Meaning | Color |
|--------|---------|-------|
| PENDING | Waiting to start | ⚪ Gray |
| RECTIFYING | Preparing/analyzing | 🟡 Orange |
| DEPLOYING | Deploying to AWS | 🔵 Blue |
| SUCCESS | Deployment complete | 🟢 Green |
| FAILED | Deployment failed | 🔴 Red |

---

## 🔐 Security Checklist

- [ ] `.env` updated with YOUR credentials
- [ ] `.env` is in `.gitignore`
- [ ] Never committed `.env` to git
- [ ] Used strong credentials
- [ ] AWS IAM permissions configured

---

## 🆘 Quick Troubleshoot

**Q: API won't start?**
```bash
# Check port 8000 isn't in use
netstat -ano | findstr :8000
```

**Q: Dashboard can't connect to API?**
- Verify API is running
- Check API_URL in `.env` is correct
- Ensure firewall allows port 8000

**Q: Missing modules?**
```bash
pip install -r requirements.txt --upgrade
```

**Q: Credentials not working?**
- Verify `.env` in project root
- Check credentials are correct
- Ensure AWS IAM permissions for Lambda

---

## 📞 Documentation

- **Full Setup:** → `SETUP.md`
- **All Environment Vars:** → `ENV_CONFIG.md`
- **Frontend Docs:** → `frontend/README.md`
- **Main README:** → `README.md`

---

## ⏱️ Typical Workflow

```
1. Update .env (1 min)
   ↓
2. Run run.bat/run.sh (2 min)
   ↓
3. Start API server (10 sec)
   ↓
4. Start Dashboard (5 sec)
   ↓
5. Upload services (POST /upload)
   ↓
6. Start migration (POST /start)
   ↓
7. Monitor in dashboard
   ↓
8. View results
```

---

**Total setup time: ~5 minutes** ⚡

Next step → Update `.env` with your AWS credentials and run `run.bat` or `bash run.sh`

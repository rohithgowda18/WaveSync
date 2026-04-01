# 🎯 START HERE

**Welcome to WaveSync!** Your integrated cloud migration system is ready.

---

## 3️⃣ Steps to Deploy (5 minutes)

### 1️⃣ Update `.env` (1 minute)
Open `WaveSync/.env` and update:
```env
AWS_ACCESS_KEY_ID=your_actual_key_id_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
```

### 2️⃣ Run Setup (2 minutes)
Choose one:
```bash
# Windows
run.bat

# Linux/macOS
bash run.sh
```

### 3️⃣ Start Services (30 seconds)
**Terminal 1:**
```bash
python src/wavesync/frontend/app.py
```

**Terminal 2:**
```bash
cd frontend
streamlit run dashboard.py
```

---

## ✨ That's It!

You now have:
- ✅ **API Server** at `http://127.0.0.1:8000`
- ✅ **Dashboard** at `http://127.0.0.1:8501`
- ✅ **API Documentation** at `http://127.0.0.1:8000/docs`

---

## 📖 Documentation

Read based on your needs:

| Time | For | Read |
|------|-----|------|
| 2 min | Quick overview | [`SUMMARY.md`](SUMMARY.md) |
| 5 min | What to do next | [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) |
| 10 min | Detailed setup | [`SETUP.md`](SETUP.md) |
| 5 min | All configuration | [`ENV_CONFIG.md`](ENV_CONFIG.md) |
| 20 min | Everything | [`README.md`](README.md) |

**Lost?** → See [`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md)

---

## 🚀 Next: Upload & Deploy

```bash
# Upload services
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{"services": ["service1", "service2"]}'

# Start migration
curl -X POST "http://127.0.0.1:8000/start"

# Monitor in dashboard: http://127.0.0.1:8501
```

---

## 🆘 Issues?

| Problem | Solution |
|---------|----------|
| API won't start | Check port 8000 is free |
| Dashboard won't connect | Verify API is running |
| Module errors | Run: `pip install -r requirements.txt` |
| More help | See [`SETUP.md#troubleshooting`](SETUP.md#troubleshooting) |

---

## ✅ Files You Need

- **`.env`** - Your AWS credentials (update this!)
- **`run.bat` or `run.sh`** - Setup script
- **`QUICK_REFERENCE.md`** - Commands & endpoints
- **`SETUP.md`** - Detailed setup guide

---

**Ready?** → Update `.env` and run your setup script above! 🎉

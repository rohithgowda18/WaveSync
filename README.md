# WaveSync - Cloud Migration Control Center

**By:** Rohith, Venkatachala, Vijay Patil, Vijay V Patil

AI-powered dependency-aware orchestration for microservice migrations to AWS.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS Account (for Lambda deployment)
- pip/virtualenv

### Setup (Windows)
```bash
# Run the quick start script
run.bat
```

### Setup (Linux/macOS)
```bash
# Run the quick start script
bash run.sh
```

### Manual Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📋 Environment Configuration

Create a `.env` file in the project root with your AWS credentials:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=eu-north-1
AWS_LAMBDA_FUNCTION=wavesync-function

# API Configuration
API_URL=http://127.0.0.1:8000
API_PORT=8000
API_HOST=127.0.0.1

# Database
DATABASE_URL=sqlite:///./test.db

# Logging
LOG_LEVEL=INFO
```

⚠️ **IMPORTANT:** Add `.env` to `.gitignore` - never commit credentials!

---

## 🏃 Running the Application

### Terminal 1: Start the API Server
```bash
# From project root
python src/wavesync/frontend/app.py
```

The API will start at `http://127.0.0.1:8000`
- View API docs: `http://127.0.0.1:8000/docs`

### Terminal 2: Start the Dashboard
```bash
# From project root
cd frontend
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📡 API Endpoints

### Deployment Pipeline
- **`POST /upload`** - Upload services for migration
  ```json
  {
    "services": ["service1", "service2", "service3"]
  }
  ```

- **`POST /start`** - Start the migration pipeline
  
- **`GET /services`** - Get status of all services

- **`GET /health`** - Health check

---

## 🏗️ Project Structure

```
WaveSync/
├── .env                          # Environment configuration (credentials)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
│
├── src/
│   └── wavesync/
│       ├── __init__.py
│       ├── main.py
│       ├── deploy.py            # AWS deployment functions (uses .env)
│       ├── agents/              # Agent logic
│       ├── api/                 # Main API endpoints
│       ├── engine/              # Graph & orchestration engine
│       └── common/              # Common utilities
│
├── frontend/                    # Frontend application
│   ├── __init__.py
│   ├── app.py                  # FastAPI migration pipeline server (uses .env)
│   ├── dashboard.py            # Streamlit monitoring dashboard
│   └── README.md               # Frontend documentation
│
├── tests/                       # Test suite
│
├── docs/                        # Documentation
│
├── run.bat                      # Windows quick start
├── run.sh                       # Linux/macOS quick start
│
└── README.md                    # This file
```

---

## 🔑 Key Features

✅ **Environment-based Configuration** - All credentials stored in `.env`  
✅ **AWS Lambda Deployment** - Automated microservice deployment  
✅ **Real-time Dashboard** - Streamlit-based monitoring interface  
✅ **Dependency Graph** - Visualize service relationships  
✅ **Health Checks** - Automatic verification after deployment  
✅ **Status Tracking** - Monitor services: PENDING → RECTIFYING → DEPLOYING → SUCCESS/FAILED

---

## 📊 Monitoring Dashboard

The Streamlit dashboard provides:
- **Metrics**: Total services, completed, running, failed
- **Progress Bar**: Overall deployment completion
- **Service List**: Real-time status for each service
- **Activity Feed**: Live deployment events
- **Status Chart**: Distribution of service states

---

## 🔐 Security Notes

- ✅ Credentials stored in `.env` (not in code)
- ✅ `.env` excluded from git repository
- ✅ Use environment variables for all sensitive data
- ✅ Never commit `.env` files to version control

---

## 🛠️ Technology Stack

- **API Framework**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **Cloud**: AWS Lambda, boto3
- **Database**: SQLAlchemy, SQLite
- **Graph**: NetworkX
- **AI**: Groq
- **Configuration**: python-dotenv

---

## 📝 License

Created for cloud migration automation and orchestration.


# WaveSync Frontend

## Components

### `app.py`
FastAPI server that manages the migration pipeline:
- `POST /upload` - Upload services for migration
- `GET /services` - Get status of all services  
- `POST /start` - Start the migration pipeline
- `GET /health` - Health check endpoint

### `dashboard.py`
Streamlit dashboard for real-time monitoring:
- Live metrics (Total, Completed, Running, Failed)
- Progress bar tracking deployment status
- Service status visualization
- Activity feed with real-time updates

## Environment Variables

Configure these in `.env`:
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `AWS_REGION` - AWS region (default: eu-north-1)
- `AWS_LAMBDA_FUNCTION` - Lambda function name (default: wavesync-function)
- `API_URL` - API endpoint for dashboard (default: http://127.0.0.1:8000)
- `API_PORT` - API server port (default: 8000)
- `API_HOST` - API server host (default: 127.0.0.1)

## Running

### Start API Server
```bash
cd src/wavesync/frontend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Start Dashboard
```bash
cd frontend
streamlit run dashboard.py
```

## API Workflow

1. Upload services: `POST /upload` with list of service names
2. Start migration: `POST /start` to begin deployment pipeline
3. Monitor status: `GET /services` to track progress
4. View in dashboard for real-time visualization

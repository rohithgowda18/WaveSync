import uvicorn
import logging
from wavesync.api.main import app

# Senior Engineer configuration: structured logging for hackathon observability
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("wavesync")

if __name__ == "__main__":
    logger.info("Starting WaveSync AI Backend Service...")
    # Run the FastAPI app via Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

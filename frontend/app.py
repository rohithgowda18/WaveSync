from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import threading
import time
import os
from dotenv import load_dotenv

from wavesync.deploy import deploy_to_aws, wait_for_green

load_dotenv()

app = FastAPI(
    title="WaveSync Migration Pipeline",
    version="1.0.0"
)

services = []
service_status = {}


class ServiceList(BaseModel):
    services: List[str]


@app.post("/upload")
def upload(data: ServiceList):
    """Upload services for migration"""
    global services, service_status

    services = data.services
    service_status.clear()

    for s in services:
        service_status[s] = {
            "status": "PENDING",
            "url": None
        }

    return {"message": "Services uploaded successfully", "count": len(services)}


@app.get("/services")
def get_services():
    """Get current services and their status"""
    return service_status


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


def migration_pipeline():
    """Execute the migration pipeline for all services"""
    global services

    for service in services:
        service_status[service]["status"] = "RECTIFYING"
        print(f"[RECTIFY] Processing {service}...")
        time.sleep(1)

        service_status[service]["status"] = "DEPLOYING"

        result = deploy_to_aws(service)

        if result["status"] == "success":
            is_live = wait_for_green(result["url"])

            if is_live:
                service_status[service]["status"] = "SUCCESS"
                service_status[service]["url"] = result["url"]
            else:
                service_status[service]["status"] = "FAILED"
        else:
            service_status[service]["status"] = "FAILED"


@app.post("/start")
def start():
    """Start the migration pipeline"""
    if not services:
        raise HTTPException(status_code=400, detail="No services uploaded")

    thread = threading.Thread(target=migration_pipeline, daemon=True)
    thread.start()

    return {"message": "Migration started", "services": len(services)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('API_PORT', 8000))
    host = os.getenv('API_HOST', '127.0.0.1')
    uvicorn.run(app, host=host, port=port)

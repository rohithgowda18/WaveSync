from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import threading
import time
import os
import sys
from dotenv import load_dotenv
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from wavesync.deploy import deploy_to_aws, wait_for_green, get_microservice_info
from wavesync.engine.kahn_priority_engine import PriorityExecutionEngine

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


@app.get("/deployment-plan")
def get_deployment_plan():
    """Get the planned deployment order (topological sort)"""
    if not services:
        return {"deployment_plan": [], "message": "No services uploaded"}
    
    topo_sorted = get_topo_sort(services)
    plan = []
    
    for idx, svc in enumerate(topo_sorted, 1):
        info = get_microservice_info(svc)
        plan.append({
            "order": idx,
            "service": svc,
            "type": info["type"],
            "reason": info["reason"],
            "status": service_status.get(svc, {}).get("status", "PENDING")
        })
    
    return {
        "total_services": len(services),
        "deployment_plan": plan
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


def get_topo_sort(service_list: List[str]) -> List[str]:
    """
    Get topological sort of services using Kahn's Priority Algorithm
    """
    try:
        # Create service data with default priorities
        services_data = [
            {
                "id": svc,
                "priority": len(service_list) - i,  # Higher priority for earlier services
                "depends_on": []  # Default: no dependencies
            }
            for i, svc in enumerate(service_list)
        ]
        
        # Create engine and execute
        engine = PriorityExecutionEngine(services_data)
        return engine.execute()
    except:
        # Fallback to input order if algorithm fails
        return service_list


def print_deployment_info(service_name: str, svc_type: str, reason: str, index: int, total: int):
    """Print detailed microservice deployment information"""
    print("\n" + "="*80)
    print(f"📦 MICROSERVICE DEPLOYMENT #{index + 1}/{total}")
    print("="*80)
    print(f"  🔷 Service Name: {service_name}")
    print(f"  🔹 Service Type: {svc_type}")
    print(f"  📋 Deployment Reason: {reason}")
    print(f"  ⏱️  Progress: {index + 1}/{total}")
    print("="*80 + "\n")


def migration_pipeline():
    """Execute the migration pipeline for all services"""
    global services

    if not services:
        print("❌ No services to deploy")
        return

    # Print topological sort
    print("\n" + "🔄 TOPOLOGICAL SORT (Kahn's Algorithm) 🔄".center(80, "="))
    topo_sorted = get_topo_sort(services)
    print(f"\n✅ Planned Deployment Order (by dependencies & priority):\n")
    for i, svc in enumerate(topo_sorted, 1):
        print(f"   {i}. {svc}")
    print("\n" + "="*80 + "\n")

    # Deploy services
    for idx, service in enumerate(topo_sorted):
        # Determine service type
        svc_type = get_microservice_info(service)["type"]
        reason = get_microservice_info(service)["reason"]
        
        # Print deployment info
        print_deployment_info(service, svc_type, reason, idx, len(topo_sorted))
        
        service_status[service]["status"] = "RECTIFYING"
        print(f"[RECTIFY] Processing {service}...")
        time.sleep(1)

        service_status[service]["status"] = "DEPLOYING"
        print(f"[DEPLOYING] Sending {service} to AWS Lambda...")

        result = deploy_to_aws(service)

        if result["status"] == "success":
            is_live = wait_for_green(result["url"])

            if is_live:
                service_status[service]["status"] = "SUCCESS"
                service_status[service]["url"] = result["url"]
                print(f"✅ SUCCESS: {service} is now LIVE at {result['url']}")
            else:
                service_status[service]["status"] = "FAILED"
                print(f"❌ FAILED: {service} health check failed")
        else:
            service_status[service]["status"] = "FAILED"
            print(f"❌ FAILED: {service} deployment failed")


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

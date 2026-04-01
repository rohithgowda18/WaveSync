from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from schemas import ServiceCreate, ServiceResponse
import crud
from models import Service
import logging

# -----------------------------
# Setup
# -----------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WaveSync Migration API",
    version="2.0.0"
)

logging.basicConfig(level=logging.INFO)

VALID_STATES = ["Pending", "Rectifying", "Deploying", "Success", "Failed"]

# -----------------------------
# DB Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Helper (IMPORTANT)
# -----------------------------
def format_service(service):
    return {
        "id": service.id,
        "name": service.name,
        "status": service.status,
        "priority": service.priority,
        "dependencies": service.dependencies.split(",") if service.dependencies else [],
        "created_at": service.created_at,
        "updated_at": service.updated_at
    }

# -----------------------------
# Upload (Optimized)
# -----------------------------
@app.post("/upload", summary="Upload microservices")
def upload_services(services: list[ServiceCreate], db: Session = Depends(get_db)):
    db_services = []

    for s in services:
        # prevent duplicates
        if db.query(Service).filter(Service.name == s.name).first():
            continue

        db_services.append(
            Service(
                name=s.name,
                priority=s.priority,
                dependencies=",".join(s.dependencies)
            )
        )

    db.bulk_save_objects(db_services)
    db.commit()

    return {"message": f"{len(db_services)} services uploaded"}

# -----------------------------
# Get Services (with filtering)
# -----------------------------
@app.get("/services")
def get_services(status: str = None, db: Session = Depends(get_db)):
    query = db.query(Service)

    if status:
        query = query.filter(Service.status == status)

    services = query.all()
    return [format_service(s) for s in services]

# -----------------------------
# Get Single Service
# -----------------------------
@app.get("/status/{service_id}")
def get_status(service_id: int, db: Session = Depends(get_db)):
    service = crud.get_service(db, service_id)

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return format_service(service)

# -----------------------------
# Update Status (validated)
# -----------------------------
@app.put("/update/{service_id}")
def update(service_id: int, status: str, db: Session = Depends(get_db)):
    if status not in VALID_STATES:
        raise HTTPException(status_code=400, detail="Invalid status")

    service = crud.update_status(db, service_id, status)

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    logging.info(f"Service {service_id} updated to {status}")

    return {"message": "Updated successfully"}

# -----------------------------
# Smart NEXT (Dependency-aware 🔥)
# -----------------------------
@app.get("/next")
def get_next(db: Session = Depends(get_db)):
    services = db.query(Service).filter(Service.status == "Pending").all()

    for service in services:
        deps = service.dependencies.split(",") if service.dependencies else []

        valid = True
        for d in deps:
            dep_service = db.query(Service).filter(Service.name == d).first()
            if dep_service and dep_service.status != "Success":
                valid = False
                break

        if valid:
            return format_service(service)

    return {"message": "No service ready"}

# -----------------------------
# Progress (Enhanced)
# -----------------------------
@app.get("/progress")
def progress(db: Session = Depends(get_db)):
    total = db.query(Service).count()
    success = db.query(Service).filter(Service.status == "Success").count()
    failed = db.query(Service).filter(Service.status == "Failed").count()

    percentage = round((success / total) * 100, 2) if total else 0

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "percentage": percentage
    }

# -----------------------------
# Reset (Demo Feature 🔥)
# -----------------------------
@app.post("/reset")
def reset(db: Session = Depends(get_db)):
    db.query(Service).update({Service.status: "Pending"})
    db.commit()
    return {"message": "Reset complete"}

# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def home():
    return {"message": "API Running 🚀"}
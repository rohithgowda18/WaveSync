from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from schemas import ServiceCreate
import crud
from models import Service
import logging
import json
from engine.dependency_discovery import scan_directory
from ai.dependency_ai import infer_dependencies

# -----------------------------
# Setup
# -----------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WaveSync Migration API",
    version="3.0.0"
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
# Helper
# -----------------------------
def format_service(service):
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "status": service.status,
        "priority": service.priority,
        "dependencies": service.dependencies.split(",") if service.dependencies else [],
        "created_at": service.created_at,
        "updated_at": service.updated_at
    }

# -----------------------------
# 🔥 ADD SINGLE SERVICE (REAL-TIME AI)
# -----------------------------
@app.post("/add-service")
def add_service(service: ServiceCreate, db: Session = Depends(get_db)):

    existing = db.query(Service).filter(Service.name == service.name).first()
    if existing:
        return {"message": "Service already exists"}

    deps = infer_dependencies(service.name, service.description)

    new_service = Service(
        name=service.name,
        description=service.description,
        priority=service.priority,
        dependencies=",".join(deps),
        status="Pending"
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return {
        "message": "Service added with AI dependencies",
        "service": format_service(new_service)
    }

# -----------------------------
# 🔥 BULK UPLOAD (AUTO AI)
# -----------------------------
@app.post("/upload")
def upload_services(services: list[ServiceCreate], db: Session = Depends(get_db)):
    count = 0

    for s in services:
        if db.query(Service).filter(Service.name == s.name).first():
            continue

        deps = infer_dependencies(s.name, s.description)

        db.add(Service(
            name=s.name,
            description=s.description,
            priority=s.priority,
            dependencies=",".join(deps),
            status="Pending"
        ))

        count += 1

    db.commit()

    return {"message": f"{count} services uploaded with AI dependencies"}

# -----------------------------
# Code-based discovery (optional)
# -----------------------------
@app.post("/discover-dependencies")
def discover_dependencies():
    return scan_directory("services_code")

@app.post("/auto-discover")
def auto_discover(db: Session = Depends(get_db)):
    results = scan_directory("services_code")

    for service_name, deps in results.items():
        service = db.query(Service).filter(Service.name == service_name).first()
        if service:
            service.dependencies = ",".join(deps)

    db.commit()
    return {"message": "Dependencies updated from code"}

# -----------------------------
# Get Services
# -----------------------------
@app.get("/services")
def get_services(status: str = None, db: Session = Depends(get_db)):
    query = db.query(Service)

    if status:
        query = query.filter(Service.status == status)

    return [format_service(s) for s in query.all()]

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
# Update Status
# -----------------------------
@app.put("/update/{service_id}")
def update(service_id: int, status: str, db: Session = Depends(get_db)):
    if status not in VALID_STATES:
        raise HTTPException(status_code=400, detail="Invalid status")

    service = crud.update_status(db, service_id, status)

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return {"message": "Updated successfully"}

# -----------------------------
# NEXT (Dependency-aware)
# -----------------------------
@app.get("/next")
def get_next(db: Session = Depends(get_db)):
    services = db.query(Service).filter(Service.status == "Pending").all()

    for service in services:
        deps = service.dependencies.split(",") if service.dependencies else []

        if all(
            db.query(Service).filter(Service.name == d, Service.status == "Success").first()
            for d in deps
        ):
            return format_service(service)

    return {"message": "No service ready"}

# -----------------------------
# Progress
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
# Seed (AI enabled)
# -----------------------------
@app.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    with open("services.json", "r") as f:
        data = json.load(f)

    count = 0
    skipped = 0

    for service in data:
        if db.query(Service).filter(Service.name == service["name"]).first():
            skipped += 1
            continue

        deps = infer_dependencies(service["name"], service["description"])

        db.add(Service(
            name=service["name"],
            description=service["description"],
            priority=service["priority"],
            dependencies=",".join(deps),
            status="Pending"
        ))

        count += 1

    db.commit()

    return {"added": count, "skipped": skipped}

# -----------------------------
# Reset
# -----------------------------
@app.post("/reset")
def reset(db: Session = Depends(get_db)):
    db.query(Service).delete()
    db.commit()
    return {"message": "Database cleared"}

@app.post("/refresh-ai")
def refresh_ai(db: Session = Depends(get_db)):
    services = db.query(Service).all()

    for service in services:
        deps = infer_dependencies(service.name, service.description)
        service.dependencies = ",".join(deps)

    db.commit()

    return {"message": "Dependencies refreshed successfully"}

# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def home():
    return {"message": "API Running 🚀"}
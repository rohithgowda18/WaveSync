from sqlalchemy.orm import Session
from models import Service
from schemas import ServiceCreate
from ai.dependency_ai import infer_dependencies

# OPTIONAL (for hybrid system)
from engine.dependency_discovery import extract_dependencies_from_text
import os


def create_service(db: Session, service: ServiceCreate):

    # 🔒 Prevent duplicate
    existing = db.query(Service).filter(Service.name == service.name).first()
    if existing:
        return existing

    # -----------------------------
    # 🔥 AI DEPENDENCIES
    # -----------------------------
    ai_deps = set(infer_dependencies(service.name, service.description))

    # -----------------------------
    # 🔍 CODE-BASED DEPENDENCIES (OPTIONAL)
    # -----------------------------
    code_deps = set()

    file_path = f"services_code/{service.name.lower()}.py"

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                code_deps = set(extract_dependencies_from_text(content))
        except Exception as e:
            print(f"Code scan failed for {service.name}: {e}")

    # -----------------------------
    # 🔥 MERGE BOTH
    # -----------------------------
    final_deps = ai_deps.union(code_deps)

    # ❌ Remove self-dependency
    if service.name in final_deps:
        final_deps.remove(service.name)

    # -----------------------------
    # 💾 SAVE
    # -----------------------------
    db_service = Service(
        name=service.name,
        description=service.description,
        priority=service.priority,
        dependencies=",".join(final_deps),
        status="Pending"
    )

    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    return db_service


# -----------------------------
# READ
# -----------------------------
def get_services(db: Session):
    return db.query(Service).all()


def get_service(db: Session, service_id: int):
    return db.query(Service).filter(Service.id == service_id).first()


# -----------------------------
# UPDATE STATUS
# -----------------------------
def update_status(db: Session, service_id: int, status: str):
    service = db.query(Service).filter(Service.id == service_id).first()

    if service:
        service.status = status
        db.commit()
        db.refresh(service)

    return service
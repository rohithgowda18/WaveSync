from sqlalchemy.orm import Session
from wavesync.api.models import Service

def create_service(db: Session, service):
    db_service = Service(
        name=service.name,
        priority=service.priority,
        dependencies=",".join(service.dependencies),
        tech_stack=service.tech_stack,
        database_type=service.database_type
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_services(db: Session):
    return db.query(Service).all()

def get_service(db: Session, service_id: int):
    return db.query(Service).filter(Service.id == service_id).first()

def update_status(db: Session, service_id: int, status: str):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service:
        service.status = status
        db.commit()
        db.refresh(service)
    return service
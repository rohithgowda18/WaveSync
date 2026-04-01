from sqlalchemy import Column, Integer, String, DateTime
from wavesync.api.database import Base
from datetime import datetime

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    status = Column(String(50), default="Pending")
    priority = Column(Integer)
    dependencies = Column(String(255))
    tech_stack = Column(String(255))
    database_type = Column(String(255))

    # NEW (IMPORTANT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
from pydantic import BaseModel
from typing import List

class ServiceCreate(BaseModel):
    name: str
    priority: int
    dependencies: List[str]
    tech_stack: str
    database_type: str

class ServiceResponse(BaseModel):
    id: int
    name: str
    status: str
    priority: int
    dependencies: str
    tech_stack: str
    database_type: str

    class Config:
        from_attributes = True
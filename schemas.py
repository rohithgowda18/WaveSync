from pydantic import BaseModel
from typing import List

class ServiceCreate(BaseModel):
    name: str
    description: str
    priority: int
    dependencies: List[str] = []

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    priority: int
    dependencies: List[str] = []

    class Config:
        from_attributes = True
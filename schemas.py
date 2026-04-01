from pydantic import BaseModel
from typing import List

class ServiceCreate(BaseModel):
    name: str
    priority: int
    dependencies: List[str]

class ServiceResponse(BaseModel):
    id: int
    name: str
    status: str
    priority: int
    dependencies: str

    class Config:
        from_attributes = True
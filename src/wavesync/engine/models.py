"""
Data models for the WaveSync Graph & Logic Engine.
Defines the schema for services and their dependencies.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Dict, Any, Optional


class ServiceNode(BaseModel):
    """
    Represents a microservice node in the migration graph.
    
    Attributes:
        id: Unique identifier for the service.
        priority: Business priority level (1-10), where 10 is highest priority.
        depends_on: List of service IDs this service depends on.
        metadata: Optional dictionary for storing additional service information.
    """

    id: str = Field(..., description="Unique identifier for the service")
    priority: int = Field(
        ...,
        description="Business priority level (1-10)",
        ge=1,
        le=10,
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="List of service IDs this service depends on",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the service",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "auth-service",
                "priority": 9,
                "depends_on": ["database"],
                "metadata": {
                    "owner": "security-team",
                    "criticality": "high",
                },
            }
        }
    )

    @field_validator("depends_on", mode="after")
    @classmethod
    def validates_no_self_dependency(cls, v, info):
        """
        Validate that a service does not depend on itself.
        
        Args:
            v: The depends_on list being validated.
            info: Information about the validation context.
            
        Raises:
            ValueError: If the service ID appears in its own depends_on list.
        """
        service_id = info.data.get("id")
        if service_id and service_id in v:
            raise ValueError(
                f"Service '{service_id}' cannot depend on itself. "
                f"Remove '{service_id}' from depends_on."
            )
        return v

    @field_validator("depends_on", mode="after")
    @classmethod
    def validates_depends_on_not_empty_strings(cls, v):
        """
        Validate that depends_on list does not contain empty strings.
        
        Args:
            v: The depends_on list being validated.
            
        Raises:
            ValueError: If any dependency ID is an empty string.
        """
        if any(dep == "" for dep in v):
            raise ValueError(
                "depends_on list contains empty strings. All dependency IDs must be non-empty."
            )
        return v

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator


class ServiceNode(BaseModel):
    """
    Data model representing a microservice node in an orchestration system.
    """
    id: str = Field(
        ..., 
        description="Unique identifier for the service"
    )
    priority: int = Field(
        ..., 
        ge=1, 
        le=10, 
        description="Priority level from 1 (highest/lowest based on system) to 10"
    )
    depends_on: List[str] = Field(
        default_factory=list, 
        description="List of service IDs this service depends on"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Optional metadata dictionary for additional configuration"
    )

    @model_validator(mode='after')
    def check_self_dependency(self):
        """
        Validates that a service does not declare a dependency on itself.
        """
        if self.id in self.depends_on:
            raise ValueError(f"Service '{self.id}' cannot depend on itself.")
        return self


# Example Usage:
if __name__ == "__main__":
    # Valid Service Node
    auth_service = ServiceNode(
        id="auth-service",
        priority=1,
        metadata={"team": "security", "timeout": 30}
    )
    print(f"Created: {auth_service.id}")

    payment_service = ServiceNode(
        id="payment-service",
        priority=2,
        depends_on=["auth-service"],
        metadata={"requires_pci": True}
    )
    print(f"Created: {payment_service.id}")

    # Invalid Service Node Example (fails validation)
    try:
        invalid_service = ServiceNode(
            id="circular-service",
            priority=5,
            depends_on=["circular-service"]
        )
    except ValueError as e:
        print(f"Validation Error caught successfully: {e}")

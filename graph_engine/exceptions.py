"""
Custom exceptions for the WaveSync Graph & Logic Engine.
"""


class MigrationCycleError(Exception):
    """
    Raised when a circular dependency is detected in the service dependency graph.
    This indicates that the migration cannot proceed as services are interdependent.
    """

    def __init__(self, cycle_services: list[str], message: str = None):
        """
        Initialize MigrationCycleError.
        
        Args:
            cycle_services: List of service IDs involved in the circular dependency.
            message: Optional custom error message.
        """
        self.cycle_services = cycle_services
        if message is None:
            message = f"Circular dependency detected involving services: {', '.join(cycle_services)}"
        super().__init__(message)


class InvalidServiceError(Exception):
    """
    Raised when service data is invalid (e.g., self-referential dependencies, missing IDs).
    """

    def __init__(self, service_id: str, reason: str):
        """
        Initialize InvalidServiceError.
        
        Args:
            service_id: ID of the problematic service.
            reason: Description of why the service is invalid.
        """
        self.service_id = service_id
        message = f"Invalid service '{service_id}': {reason}"
        super().__init__(message)

"""
The WaveSync Orchestrator - Main entry point for the priority-weighted DAG engine.
Now modularized into DAGBuilder and Scheduler for scalability.
"""

from typing import List, Dict
from wavesync.engine.models import ServiceNode
from wavesync.engine.dag_builder import DAGBuilder
from wavesync.engine.scheduler import Scheduler

class WaveSyncOrchestrator:
    """
    Main orchestrator that coordinates graph construction and sequencing.
    """

    def __init__(self, services: List[ServiceNode]):
        if not services:
            raise ValueError("Services list cannot be empty")

        self.services = services
        self.builder = DAGBuilder(services)
        self.scheduler = Scheduler(self.builder.graph, self.builder.service_map)
        
        self.graph = self.builder.graph
        self._service_map = self.builder.service_map
        self._execution_sequence: List[str] = []

    def validate_dag(self) -> None:
        self.builder.validate_dag()

    def get_serial_sequence(self) -> List[str]:
        self._execution_sequence = self.scheduler.get_serial_sequence()
        return self._execution_sequence

    def get_execution_plan(self) -> Dict[str, any]:
        if not self._execution_sequence:
            self.get_serial_sequence()
        return self.scheduler.get_execution_plan(self._execution_sequence)

    def _calculate_migration_score(self, service_id: str) -> float:
        """Kept for backward compatibility if needed, but logic is in scheduler."""
        return self.scheduler.calculate_score(service_id)

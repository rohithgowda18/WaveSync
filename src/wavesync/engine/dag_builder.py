"""
WaveSync AI — DAG Builder
Handles validation and construction of the Directed Acyclic Graph (DAG) for service orchestration.
"""

import networkx as nx
from typing import List, Dict, Set
from wavesync.engine.models import ServiceNode
from wavesync.engine.exceptions import MigrationCycleError, InvalidServiceError

class DAGBuilder:
    """Component responsible for building and validating the dependency graph."""

    def __init__(self, services: List[ServiceNode]):
        self.services = services
        self.service_map: Dict[str, ServiceNode] = {}
        self.graph: nx.DiGraph = nx.DiGraph()
        
        self._validate_and_build_service_map()
        self._build_graph()
        self.validate_dag()

    def _validate_and_build_service_map(self) -> None:
        seen_ids: Set[str] = set()
        for service in self.services:
            if service.id in seen_ids:
                raise InvalidServiceError(service.id, f"Duplicate service ID '{service.id}'")
            for dep_id in service.depends_on:
                if dep_id == service.id:
                    raise InvalidServiceError(service.id, "Service depends on itself")
            seen_ids.add(service.id)
            self.service_map[service.id] = service

        for service in self.services:
            for dep_id in service.depends_on:
                if dep_id not in self.service_map:
                    raise InvalidServiceError(service.id, f"Depends on non-existent service '{dep_id}'")

    def _build_graph(self) -> None:
        for service in self.services:
            self.graph.add_node(
                service.id,
                priority=service.priority,
                metadata=service.metadata,
            )
        for service in self.services:
            for dep_id in service.depends_on:
                self.graph.add_edge(dep_id, service.id)

    def validate_dag(self) -> None:
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                cycle_services = cycles[0]
                raise MigrationCycleError(
                    cycle_services,
                    f"Circular dependency detected: {' -> '.join(cycle_services)} -> {cycle_services[0]}",
                )
            raise MigrationCycleError([], "Circular dependency detected")

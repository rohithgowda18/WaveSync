"""
The WaveSync Orchestrator - Core engine for priority-weighted DAG-based service orchestration.
Implements a deterministic, constraint-satisfaction approach to microservice migration sequencing.
"""

import heapq
from collections import defaultdict
from typing import List, Dict, Set, Tuple
import networkx as nx

from wavesync.engine.models import ServiceNode
from wavesync.engine.exceptions import MigrationCycleError, InvalidServiceError


class WaveSyncOrchestrator:
    """
    Orchestrates the serial execution sequence of microservices based on dependencies and priorities.
    
    Uses a Priority-Weighted DAG approach with a modified Kahn's algorithm that considers both
    business priority and service criticality (out-degree) when determining execution order.
    
    Mathematical Heuristic:
        Migration Score (S) = (BusinessPriority × 0.7) + (OutDegree × 0.3)
        
    Where:
        - BusinessPriority: User-defined priority (1-10)
        - OutDegree: Number of downstream services dependent on this service
    """

    PRIORITY_WEIGHT = 0.7
    OUT_DEGREE_WEIGHT = 0.3

    def __init__(self, services: List[ServiceNode]):
        """
        Initialize the orchestrator with a list of services.
        
        Args:
            services: List of ServiceNode objects representing the services to orchestrate.
            
        Raises:
            ValueError: If services list is empty.
            InvalidServiceError: If any service has invalid data.
        """
        if not services:
            raise ValueError("Services list cannot be empty")

        self.services = services
        self._service_map: Dict[str, ServiceNode] = {}
        self.graph: nx.DiGraph = nx.DiGraph()
        self._execution_sequence: List[str] = []

        # Validate and build the service map
        self._validate_and_build_service_map()

        # Build the dependency graph
        self._build_graph()

        # Validate that the graph is a DAG
        self.validate_dag()

    def _validate_and_build_service_map(self) -> None:
        """
        Validate service data and build an internal mapping.
        
        Raises:
            InvalidServiceError: If duplicate IDs or invalid data is found.
        """
        seen_ids: Set[str] = set()

        for service in self.services:
            if service.id in seen_ids:
                raise InvalidServiceError(
                    service.id,
                    f"Duplicate service ID '{service.id}'",
                )

            # Validate that all dependencies reference existing services
            for dep_id in service.depends_on:
                if dep_id == service.id:
                    raise InvalidServiceError(
                        service.id,
                        f"Service depends on itself",
                    )

            seen_ids.add(service.id)
            self._service_map[service.id] = service

        # Validate that all dependencies point to existing services
        for service in self.services:
            for dep_id in service.depends_on:
                if dep_id not in self._service_map:
                    raise InvalidServiceError(
                        service.id,
                        f"Depends on non-existent service '{dep_id}'",
                    )

    def _build_graph(self) -> None:
        """
        Build the directed graph representing service dependencies.
        
        Adds nodes for each service and directed edges from dependencies to services.
        Edge direction: dependency_service -> dependent_service
        """
        # Add all services as nodes
        for service in self.services:
            self.graph.add_node(
                service.id,
                priority=service.priority,
                metadata=service.metadata,
            )

        # Add edges for dependencies
        # If Service A depends on Service B, add edge B -> A
        # (A is "blocked" until B completes)
        for service in self.services:
            for dep_id in service.depends_on:
                self.graph.add_edge(dep_id, service.id)

    def validate_dag(self) -> None:
        """
        Validate that the graph is acyclic (no circular dependencies).
        
        Raises:
            MigrationCycleError: If a cycle is detected, with information about the cycle.
        """
        if not nx.is_directed_acyclic_graph(self.graph):
            # Find and report the cycle
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                cycle_services = cycles[0]
                raise MigrationCycleError(
                    cycle_services,
                    f"Circular dependency detected: {' -> '.join(cycle_services)} -> {cycle_services[0]}",
                )
            else:
                raise MigrationCycleError(
                    [],
                    "Circular dependency detected in the service graph",
                )

    def _calculate_migration_score(self, service_id: str) -> float:
        """
        Calculate the priority-weighted migration score for a service.
        
        Formula: S = (BusinessPriority × 0.7) + (OutDegree × 0.3)
        
        Args:
            service_id: The ID of the service to score.
            
        Returns:
            The calculated migration score.
        """
        service = self._service_map[service_id]
        business_priority = service.priority
        out_degree = self.graph.out_degree(service_id)

        score = (
            business_priority * self.PRIORITY_WEIGHT
            + out_degree * self.OUT_DEGREE_WEIGHT
        )

        return score

    def get_serial_sequence(self) -> List[str]:
        """
        Generate the deterministic serial execution sequence using a modified Kahn's algorithm.
        
        The algorithm:
        1. Identifies all services with no dependencies (in-degree == 0)
        2. Pushes them to a max-heap ordered by migration score
        3. Iteratively:
            - Pops the highest-scoring ready service
            - Adds it to the execution sequence
            - Updates dependent services' in-degrees
            - Adds newly ready services to the heap
        
        Returns:
            List of service IDs in deterministic execution order.
            
        Raises:
            RuntimeError: If not all services could be sequenced (shouldn't happen if DAG is valid).
        """
        # Calculate in-degrees for all nodes
        in_degree: Dict[str, int] = {node: 0 for node in self.graph.nodes()}
        for node in self.graph.nodes():
            in_degree[node] = self.graph.in_degree(node)

        # Find all nodes with in-degree 0 (ready to execute)
        ready_services: List[Tuple[float, str]] = []
        for service_id in self.graph.nodes():
            if in_degree[service_id] == 0:
                score = self._calculate_migration_score(service_id)
                # Use negative score for max-heap behavior (heapq is min-heap)
                heapq.heappush(ready_services, (-score, service_id))

        execution_sequence: List[str] = []

        # Process services by score
        while ready_services:
            # Pop the service with highest migration score
            neg_score, service_id = heapq.heappop(ready_services)
            execution_sequence.append(service_id)

            # Update in-degrees of dependent services
            for dependent_id in self.graph.successors(service_id):
                in_degree[dependent_id] -= 1

                # If a dependent service is now ready, add it to the heap
                if in_degree[dependent_id] == 0:
                    dep_score = self._calculate_migration_score(dependent_id)
                    heapq.heappush(ready_services, (-dep_score, dependent_id))

        # Verify that all services were sequenced
        if len(execution_sequence) != len(self.graph.nodes()):
            raise RuntimeError(
                "Failed to sequence all services. This should not happen if the DAG is valid."
            )

        self._execution_sequence = execution_sequence
        return execution_sequence

    def get_execution_plan(self) -> Dict[str, any]:
        """
        Get a comprehensive execution plan with metadata.
        
        Returns a detailed plan including the sequence, critical path, and graph metrics.
        
        Returns:
            Dictionary containing:
                - sequence: List of service IDs in execution order
                - graph_metrics: Information about the graph structure
                - service_details: Details about each service in execution order
        """
        if not self._execution_sequence:
            self.get_serial_sequence()

        # Calculate critical path depth
        critical_path_length = nx.dag_longest_path_length(self.graph) + 1

        graph_metrics = {
            "total_services": len(self.graph.nodes()),
            "total_dependencies": len(self.graph.edges()),
            "critical_path_depth": critical_path_length,
        }

        service_details = []
        for idx, service_id in enumerate(self._execution_sequence):
            service = self._service_map[service_id]
            service_details.append({
                "sequence_position": idx + 1,
                "service_id": service_id,
                "priority": service.priority,
                "in_degree": self.graph.in_degree(service_id),
                "out_degree": self.graph.out_degree(service_id),
                "score": self._calculate_migration_score(service_id),
                "dependencies": service.depends_on,
                "dependents": list(self.graph.successors(service_id)),
                "metadata": service.metadata,
            })

        return {
            "sequence_order": self._execution_sequence,
            "graph_metrics": graph_metrics,
            "service_details": service_details,
        }

    def is_idempotent(self, partially_sequenced: List[str]) -> List[str]:
        """
        Re-calculate sequence for remaining services after partial execution.
        
        This enables the engine to resume from any point in the execution sequence.
        
        Args:
            partially_sequenced: Services already processed/executed.
            
        Returns:
            List of remaining services in the correct execution order.
            
        Raises:
            ValueError: If a service in partially_sequenced doesn't exist or is out of order.
        """
        # Validate that all services in partially_sequenced exist
        for service_id in partially_sequenced:
            if service_id not in self._service_map:
                raise ValueError(f"Unknown service ID: {service_id}")

        # Find services not yet processed
        processed_set = set(partially_sequenced)
        remaining_services = [
            service for service in self.services
            if service.id not in processed_set
        ]

        if not remaining_services:
            return []

        # For remaining services, remove dependencies to already-processed services
        # because those dependencies are satisfied
        updated_services = []
        for service in remaining_services:
            # Keep only dependencies that are in the remaining services
            remaining_deps = [
                dep for dep in service.depends_on
                if dep not in processed_set
            ]
            updated_service = ServiceNode(
                id=service.id,
                priority=service.priority,
                depends_on=remaining_deps,
                metadata=service.metadata,
            )
            updated_services.append(updated_service)

        # Create a new orchestrator for remaining services
        remaining_orchestrator = WaveSyncOrchestrator(updated_services)
        return remaining_orchestrator.get_serial_sequence()

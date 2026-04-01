"""
WaveSync AI — Scheduler
Handles the priority-weighted sequencing logic from a pre-built DAG.
"""

import heapq
import networkx as nx
from typing import List, Dict, Tuple
from wavesync.engine.models import ServiceNode

class Scheduler:
    """Component responsible for calculating migration priority and sequencing."""

    PRIORITY_WEIGHT = 0.7
    OUT_DEGREE_WEIGHT = 0.3

    def __init__(self, graph: nx.DiGraph, service_map: Dict[str, ServiceNode]):
        self.graph = graph
        self.service_map = service_map

    def calculate_score(self, service_id: str) -> float:
        service = self.service_map[service_id]
        business_priority = service.priority
        out_degree = self.graph.out_degree(service_id)

        return (
            business_priority * self.PRIORITY_WEIGHT
            + out_degree * self.OUT_DEGREE_WEIGHT
        )

    def get_serial_sequence(self) -> List[str]:
        in_degree: Dict[str, int] = {node: self.graph.in_degree(node) for node in self.graph.nodes()}
        
        ready_services: List[Tuple[float, str]] = []
        for service_id in self.graph.nodes():
            if in_degree[service_id] == 0:
                score = self.calculate_score(service_id)
                heapq.heappush(ready_services, (-score, service_id))

        execution_sequence: List[str] = []
        while ready_services:
            neg_score, service_id = heapq.heappop(ready_services)
            execution_sequence.append(service_id)

            for dependent_id in self.graph.successors(service_id):
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    dep_score = self.calculate_score(dependent_id)
                    heapq.heappush(ready_services, (-dep_score, dependent_id))

        if len(execution_sequence) != len(self.graph.nodes()):
            raise RuntimeError("Cycle or dependency error during sequencing")

        return execution_sequence

    def get_execution_plan(self, execution_sequence: List[str]) -> Dict[str, any]:
        critical_path_length = nx.dag_longest_path_length(self.graph) + 1
        
        graph_metrics = {
            "total_services": len(self.graph.nodes()),
            "total_dependencies": len(self.graph.edges()),
            "critical_path_depth": critical_path_length,
        }

        service_details = []
        for idx, service_id in enumerate(execution_sequence):
            service = self.service_map[service_id]
            service_details.append({
                "sequence_position": idx + 1,
                "service_id": service_id,
                "priority": service.priority,
                "in_degree": self.graph.in_degree(service_id),
                "out_degree": self.graph.out_degree(service_id),
                "score": self.calculate_score(service_id),
                "dependencies": service.depends_on,
                "dependents": list(self.graph.successors(service_id)),
                "metadata": service.metadata,
            })

        return {
            "sequence_order": execution_sequence,
            "graph_metrics": graph_metrics,
            "service_details": service_details,
        }

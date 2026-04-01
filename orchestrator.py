import networkx as nx
from typing import List, Set, Dict, Any, Optional

from service_node import ServiceNode
from graph_validator import validate_dag, CycleError


class WaveSyncOrchestrator:
    """
    Complete Orchestrator for managing microservice dependencies.
    Models the system as a Directed Acyclic Graph (DAG), enabling 
    topological sorting, priority-based execution, and restart capabilities.
    Built for integration into async/FastAPI backend architectures.
    """

    def __init__(self, services: List[ServiceNode]):
        """
        Initializes the orchestrator with the provided list of service definitions.
        """
        self.services: Dict[str, ServiceNode] = {s.id: s for s in services}
        self.graph = nx.DiGraph()

    def build_graph(self) -> None:
        """
        Constructs the internal DAG from the provided ServiceNodes dynamically.
        Creates edges in the format: dependency -> service.
        """
        self.graph.clear()

        # Step 1: Initialize all vertices
        for s_id, service in self.services.items():
            self.graph.add_node(
                s_id,
                priority=service.priority,
                metadata=service.metadata or {}
            )

        # Step 2: Establish dependency edges
        for s_id, service in self.services.items():
            for dependency_id in service.depends_on:
                if dependency_id not in self.services:
                    raise ValueError(f"Failed to find dependency '{dependency_id}' for service '{s_id}'")
                self.graph.add_edge(dependency_id, s_id)

    def validate_graph(self) -> bool:
        """
        Validates the underlying graph topology checking for cycles mapping
        back to the external validation module natively processing networkx DiGraphs.
        """
        # Exception `CycleError` propagates natively if a cycle exists
        return validate_dag(self.graph)

    def calculate_score(self, node_id: str) -> int:
        """
        Resolves the priority integer score to deterministically break ties during
        the Topological Sort. 
        Note: The standard assumes numerical ascending sort (priority 1 > priority 10).
        """
        node_data = self.graph.nodes[node_id]
        return node_data.get('priority', 10)  # Default fallback priority is lowest

    def get_execution_plan(self, completed_nodes: Optional[Set[str]] = None) -> List[str]:
        """
        Produces the chronological execution timeline. Includes restart/resume semantics
        by intelligently pruning branches of services marked complete.

        Args:
            completed_nodes: Set of node IDs already executed.

        Returns:
            List[str]: Ordered execution node stack honoring dependencies and priority.
        """
        # Isolate state via working sandbox copy
        working_graph = self.graph.copy()

        # Prune already resolved nodes and their incoming/outgoing edges.
        if completed_nodes:
            for node in completed_nodes:
                if node in working_graph:
                    working_graph.remove_node(node)

        # Re-assert valid constraints prior to resolution
        if not nx.is_directed_acyclic_graph(working_graph):
            raise CycleError("Graph topology violation detected dynamically post-pruning.")

        # Lexicographical topological sort natively solves execution DAG generation
        # It honors tree dependencies vertically, utilizing our metric lambda for horizontal ordering.
        execution_order = list(nx.lexicographical_topological_sort(
            working_graph,
            key=self.calculate_score
        ))

        return execution_order

    def get_critical_path(self) -> List[str]:
        """
        Determines the absolute critical path bottlenecks utilizing standard
        DAG Longest Path weighting. Simulates weights assuming an abstract `duration` 
        metatag field natively or defaulting linearly.
        """
        working_graph = self.graph.copy()

        # Inject dynamic path weights via destination node context duration estimation
        for src, dest in working_graph.edges():
            dest_data = working_graph.nodes[dest]
            meta = dest_data.get('metadata', {})
            duration = meta.get('duration_ms', 1) if isinstance(meta, dict) else 1
            working_graph[src][dest]['weight'] = duration

        try:
            return nx.dag_longest_path(working_graph, weight='weight')
        except nx.NetworkXUnfeasible:
            return []

    def get_summary(self) -> Dict[str, Any]:
        """
        Yields serialized health metadata statistics optimal for REST endpoints.
        """
        # Ensure Graph is built
        if self.graph.number_of_nodes() == 0 and len(self.services) > 0:
            self.build_graph()

        critical_path = self.get_critical_path()

        return {
            "orchestrator_status": "ready",
            "total_services_registered": self.graph.number_of_nodes(),
            "total_dependency_edges": self.graph.number_of_edges(),
            "is_valid_dag_topology": nx.is_directed_acyclic_graph(self.graph),
            "critical_path_nodes": critical_path,
            "critical_path_depth": len(critical_path)
        }


# ==========================================
# Rapid Integration Diagnostics Test Suite
# ==========================================
if __name__ == "__main__":
    from pprint import pprint

    # Setting up an advanced dynamic environment matching FastAPI load
    s1 = ServiceNode(id="cache-server", priority=2, metadata={"duration_ms": 50})
    s2 = ServiceNode(id="database", priority=1, metadata={"duration_ms": 200})
    s3 = ServiceNode(id="auth-module", priority=5, depends_on=["database", "cache-server"])
    s4 = ServiceNode(id="billing-worker", priority=3, depends_on=["auth-module"], metadata={"duration_ms": 300})
    s5 = ServiceNode(id="notification", priority=1, depends_on=["billing-worker"])
    s6 = ServiceNode(id="analytics", priority=10, depends_on=["database"]) # Low priority analytics

    # Build the Orchestrator Instance
    orchestrator = WaveSyncOrchestrator(services=[s1, s2, s3, s4, s5, s6])
    
    # 1. Build and Validate
    orchestrator.build_graph()
    orchestrator.validate_graph()
    
    # 2. Extract Data Outputs
    print("--- Full Initial Execution Plan ---")
    print(orchestrator.get_execution_plan())

    print("\n--- Restart Execution Plan (Skipping completed Database/Cache) ---")
    print(orchestrator.get_execution_plan(completed_nodes={"database", "cache-server"}))

    print("\n--- System Metrics / Graph Summary ---")
    pprint(orchestrator.get_summary())

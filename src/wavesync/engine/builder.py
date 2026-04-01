import networkx as nx
from typing import List
from wavesync.engine.models import ServiceNode

def build_service_dag(services: List[ServiceNode]) -> nx.DiGraph:
    """
    Builds a Directed Acyclic Graph (DAG) using networkx based on a list of service nodes.
    
    Args:
        services (List[ServiceNode]): A list of ServiceNode object instances.
        
    Returns:
        nx.DiGraph: A directed graph where edges represent execution dependencies 
                    (dependency -> dependent_service).
    """
    G = nx.DiGraph()
    
    # 1. Add nodes dynamically for 50+ services efficiently
    # We store the priority and metadata in the graph node attributes for easy access later
    for service in services:
        G.add_node(
            service.id, 
            priority=service.priority, 
            metadata=service.metadata
        )
        
    # 2. Add edges dynamically without hardcoding
    # Edge format: Dependency -> Service 
    # (e.g. if auth-service depends on config-service -> edge goes from config-service to auth-service)
    for service in services:
        for dependency in service.depends_on:
            # networkx automatically adds the `dependency` node if it doesn't already exist
            G.add_edge(dependency, service.id)
            
    # Optional graph validation: verify if the formed structure is truly acyclic
    if not nx.is_directed_acyclic_graph(G):
        cycles = list(nx.simple_cycles(G))
        raise ValueError(f"Circular dependency detected in the services graph! Cycles found: {cycles}")
        
    return G


# Example testing logic
if __name__ == "__main__":
    s1 = ServiceNode(id="config", priority=1)
    s2 = ServiceNode(id="database", priority=1, depends_on=["config"])
    s3 = ServiceNode(id="auth", priority=3, depends_on=["database", "config"])
    s4 = ServiceNode(id="billing", priority=5, depends_on=["auth"])
    
    microservices = [s1, s2, s3, s4]
    
    # Build the DAG
    dag = build_service_dag(microservices)
    
    print(f"Graph nodes: {dag.nodes(data=True)}")
    print(f"Graph edges: {dag.edges()}")
    print("Topological Sort (Execution Order):", list(nx.topological_sort(dag)))

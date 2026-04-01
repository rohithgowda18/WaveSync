import networkx as nx

class CycleError(Exception):
    """Exception raised when a cycle is detected in a directed graph."""
    
    def __init__(self, message: str, cycles: list = None):
        super().__init__(message)
        self.cycles = cycles or []


def validate_dag(graph: nx.DiGraph) -> bool:
    """
    Validates whether the given directed graph is acyclic (no circular dependencies).
    
    Args:
        graph (nx.DiGraph): The networkx directed graph to validate.
        
    Raises:
        CycleError: If one or more cycles are detected, detailing the exact cycle path(s).
        TypeError: If the input is not a networkx DiGraph.
        
    Returns:
        bool: True if the graph is a valid, acyclic DAG.
    """
    if not isinstance(graph, nx.DiGraph):
        raise TypeError(f"Expected a networkx.DiGraph, but got {type(graph).__name__}")

    # Check for cycles efficiently
    if not nx.is_directed_acyclic_graph(graph):
        # Extract the cycles if any exist
        cycles = list(nx.simple_cycles(graph))
        
        # Format cycle paths beautifully for the error message
        # E.g. ['A', 'B', 'C'] becomes 'A -> B -> C -> A'
        formatted_paths = [
            " -> ".join(map(str, cycle + [cycle[0]])) 
            for cycle in cycles
        ]
        
        paths_str = "\n  - ".join([""] + formatted_paths)
        error_msg = f"Circular dependency detected in the network!{paths_str}"
        
        raise CycleError(error_msg, cycles=cycles)
        
    return True


# Example Usage & Testing
if __name__ == "__main__":
    # Test Case 1: Valid DAG
    valid_graph = nx.DiGraph()
    valid_graph.add_edges_from([("A", "B"), ("B", "C"), ("A", "C")])
    print("Validating acyclic graph...")
    assert validate_dag(valid_graph) is True
    print("Successfully validated DAG!\n")
    
    # Test Case 2: Graph with a Cycle
    invalid_graph = nx.DiGraph()
    invalid_graph.add_edges_from([
        ("auth-service", "database-service"), 
        ("database-service", "billing-service"), 
        ("billing-service", "auth-service")  # This creates a cycle
    ])
    
    print("Validating cyclic graph...")
    try:
        validate_dag(invalid_graph)
    except CycleError as e:
        print(f"Caught CycleError successfully:\n{e}")

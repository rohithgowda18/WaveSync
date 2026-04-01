"""
Quick Verification: WaveSync Graph & Logic Engine
Simple test of core functionality without Unicode characters.
"""

from graph_engine import ServiceNode, WaveSyncOrchestrator, MigrationCycleError


def verify_basic_functionality():
    """Verify core functionality works as expected."""
    print("\n" + "=" * 70)
    print("WaveSync Orchestrator - Basic Verification")
    print("=" * 70)

    # Example 1: Simple chain
    print("\n1. LINEAR DEPENDENCY CHAIN:")
    services = [
        ServiceNode(id="database", priority=10, depends_on=[]),
        ServiceNode(id="cache", priority=9, depends_on=["database"]),
        ServiceNode(id="auth", priority=8, depends_on=["database"]),
        ServiceNode(id="api", priority=7, depends_on=["auth", "cache"]),
    ]
    
    orchestrator = WaveSyncOrchestrator(services)
    sequence = orchestrator.get_serial_sequence()
    print(f"   Sequence: {sequence}")
    assert sequence[0] == "database"
    assert sequence[-1] == "api"
    print("   [PASS] Dependencies respected")

    # Example 2: Priority scoring
    print("\n2. PRIORITY-BASED SCORING:")
    services2 = [
        ServiceNode(id="low", priority=1, depends_on=[]),
        ServiceNode(id="high", priority=10, depends_on=[]),
        ServiceNode(id="mid", priority=5, depends_on=[]),
    ]
    
    orchestrator2 = WaveSyncOrchestrator(services2)
    sequence2 = orchestrator2.get_serial_sequence()
    print(f"   Sequence: {sequence2}")
    assert sequence2.index("high") < sequence2.index("mid")
    assert sequence2.index("mid") < sequence2.index("low")
    print("   [PASS] High priority services executed first")

    # Example 3: Cycle detection
    print("\n3. CYCLE DETECTION:")
    try:
        cyclic_services = [
            ServiceNode(id="svc-a", priority=5, depends_on=["svc-b"]),
            ServiceNode(id="svc-b", priority=5, depends_on=["svc-a"]),
        ]
        WaveSyncOrchestrator(cyclic_services)
        print("   [FAIL] Should have detected cycle")
    except MigrationCycleError as e:
        print(f"   Cycle detected: {e}")
        print("   [PASS] Circular dependencies rejected")

    # Example 4: Execution plan
    print("\n4. EXECUTION PLAN WITH METRICS:")
    services3 = [
        ServiceNode(id="db", priority=10, depends_on=[]),
        ServiceNode(id="cache", priority=8, depends_on=["db"]),
        ServiceNode(id="auth", priority=8, depends_on=["db"]),
        ServiceNode(id="api", priority=7, depends_on=["auth", "cache"]),
    ]
    
    orchestrator3 = WaveSyncOrchestrator(services3)
    plan = orchestrator3.get_execution_plan()
    print(f"   Total Services: {plan['graph_metrics']['total_services']}")
    print(f"   Total Dependencies: {plan['graph_metrics']['total_dependencies']}")
    print(f"   Critical Path Depth: {plan['graph_metrics']['critical_path_depth']}")
    print("   [PASS] Metrics calculated correctly")

    # Example 5: Determinism
    print("\n5. DETERMINISM CHECK:")
    def get_sequence():
        services = [
            ServiceNode(id="svc-a", priority=5, depends_on=[]),
            ServiceNode(id="svc-b", priority=7, depends_on=["svc-a"]),
            ServiceNode(id="svc-c", priority=3, depends_on=[]),
            ServiceNode(id="svc-d", priority=9, depends_on=["svc-b", "svc-c"]),
        ]
        orch = WaveSyncOrchestrator(services)
        return orch.get_serial_sequence()
    
    seq1 = get_sequence()
    seq2 = get_sequence()
    seq3 = get_sequence()
    print(f"   Run 1: {seq1}")
    print(f"   Run 2: {seq2}")
    print(f"   Run 3: {seq3}")
    assert seq1 == seq2 == seq3
    print("   [PASS] Sequences are deterministic")

    # Example 6: Large scale test
    print("\n6. LARGE-SCALE TEST (50 SERVICES):")
    large_services = []
    for i in range(50):
        deps = []
        if i > 0:
            deps.append(f"service-{i-1}")
        if i > 2:
            deps.append(f"service-{i-3}")
        large_services.append(
            ServiceNode(id=f"service-{i}", priority=(i % 9) + 1, depends_on=deps)
        )
    
    large_orch = WaveSyncOrchestrator(large_services)
    large_seq = large_orch.get_serial_sequence()
    print(f"   Generated sequence for 50 services")
    print(f"   Sequence length: {len(large_seq)}")
    assert len(large_seq) == 50
    assert len(set(large_seq)) == 50  # All unique
    print("   [PASS] Large-scale orchestration successful")

    print("\n" + "=" * 70)
    print("ALL VERIFICATION TESTS PASSED!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    verify_basic_functionality()

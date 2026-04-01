"""
Example Usage: WaveSync Graph & Logic Engine
Demonstrates various scenarios and use cases for the orchestrator.
"""

from graph_engine import ServiceNode, WaveSyncOrchestrator


def example_1_simple_chain():
    """
    Example 1: Simple linear dependency chain.
    Perfect for understanding basic functionality.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Linear Dependency Chain")
    print("=" * 70)

    services = [
        ServiceNode(id="prepare-environment", priority=10, depends_on=[]),
        ServiceNode(id="deploy-database", priority=9, depends_on=["prepare-environment"]),
        ServiceNode(id="deploy-cache", priority=8, depends_on=["deploy-database"]),
        ServiceNode(id="deploy-api", priority=7, depends_on=["deploy-cache"]),
    ]

    orchestrator = WaveSyncOrchestrator(services)
    sequence = orchestrator.get_serial_sequence()

    print(f"✓ Execution Sequence:")
    for idx, service_id in enumerate(sequence, 1):
        print(f"  {idx}. {service_id}")


def example_2_diamond_pattern():
    """
    Example 2: Diamond dependency pattern.
    Shows how the engine handles multiple dependencies converging.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Diamond Dependency Pattern")
    print("=" * 70)

    services = [
        ServiceNode(id="infrastructure", priority=10, depends_on=[]),
        ServiceNode(id="authentication", priority=8, depends_on=["infrastructure"]),
        ServiceNode(id="logging", priority=8, depends_on=["infrastructure"]),
        ServiceNode(id="monitoring", priority=8, depends_on=["infrastructure"]),
        ServiceNode(id="api-gateway", priority=9, depends_on=["authentication", "logging", "monitoring"]),
    ]

    orchestrator = WaveSyncOrchestrator(services)
    plan = orchestrator.get_execution_plan()

    print(f"✓ Total Services: {plan['graph_metrics']['total_services']}")
    print(f"✓ Total Dependencies: {plan['graph_metrics']['total_dependencies']}")
    print(f"✓ Critical Path Depth: {plan['graph_metrics']['critical_path_depth']}")
    print(f"\n✓ Execution Sequence:")
    for detail in plan['service_details']:
        print(f"  {detail['sequence_position']}. {detail['service_id']}")
        print(f"     Priority: {detail['priority']}, Score: {detail['score']:.2f}")


def example_3_priority_optimization():
    """
    Example 3: Priority-based optimization.
    Demonstrates how the engine prioritizes high-importance services.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Priority-Based Service Optimization")
    print("=" * 70)

    services = [
        ServiceNode(id="low-priority-service", priority=2, depends_on=[]),
        ServiceNode(id="medium-priority-service", priority=5, depends_on=[]),
        ServiceNode(id="high-priority-service", priority=10, depends_on=[]),
        ServiceNode(id="critical-infrastructure", priority=9, depends_on=["high-priority-service"]),
    ]

    orchestrator = WaveSyncOrchestrator(services)
    sequence = orchestrator.get_serial_sequence()

    print(f"✓ Execution Order (High Priority First):")
    for idx, service_id in enumerate(sequence, 1):
        score = orchestrator._calculate_migration_score(service_id)
        service = orchestrator._service_map[service_id]
        print(f"  {idx}. {service_id} (Priority: {service.priority}, Score: {score:.2f})")


def example_4_complex_microservices():
    """
    Example 4: Complex microservices architecture.
    Simulates a realistic 25-service cloud environment.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Complex Microservices Architecture (25 Services)")
    print("=" * 70)

    services = [
        # Foundation layer
        ServiceNode(id="cloud-infrastructure", priority=10, depends_on=[]),
        ServiceNode(id="network-setup", priority=10, depends_on=[]),
        ServiceNode(id="storage-setup", priority=9, depends_on=["cloud-infrastructure"]),

        # Database layer
        ServiceNode(id="primary-database", priority=9, depends_on=["storage-setup"]),
        ServiceNode(id="cache-layer", priority=8, depends_on=["primary-database"]),
        ServiceNode(id="search-engine", priority=7, depends_on=["storage-setup"]),

        # Security layer
        ServiceNode(id="identity-provider", priority=9, depends_on=["primary-database"]),
        ServiceNode(id="secrets-manager", priority=9, depends_on=["identity-provider"]),

        # Core services
        ServiceNode(id="auth-service", priority=9, depends_on=["identity-provider", "secrets-manager"]),
        ServiceNode(id="user-service", priority=8, depends_on=["auth-service", "primary-database"]),
        ServiceNode(id="product-service", priority=7, depends_on=["primary-database", "search-engine"]),
        ServiceNode(id="order-service", priority=8, depends_on=["product-service", "user-service"]),
        ServiceNode(id="payment-service", priority=9, depends_on=["order-service", "secrets-manager"]),

        # Integration layer
        ServiceNode(id="message-broker", priority=8, depends_on=["network-setup"]),
        ServiceNode(id="notification-service", priority=6, depends_on=["message-broker"]),
        ServiceNode(id="analytics-service", priority=5, depends_on=["primary-database"]),

        # API layer
        ServiceNode(id="api-gateway", priority=9, depends_on=["auth-service", "payment-service"]),
        ServiceNode(id="public-api", priority=8, depends_on=["api-gateway", "user-service"]),

        # Observability
        ServiceNode(id="monitoring-service", priority=7, depends_on=["cache-layer"]),
        ServiceNode(id="logging-service", priority=7, depends_on=["storage-setup"]),
        ServiceNode(id="tracing-service", priority=6, depends_on=["message-broker"]),

        # Admin and utility services
        ServiceNode(id="admin-portal", priority=6, depends_on=["public-api", "auth-service"]),
        ServiceNode(id="configuration-service", priority=8, depends_on=["secrets-manager"]),
        ServiceNode(id="backup-service", priority=7, depends_on=["primary-database", "storage-setup"]),
    ]

    orchestrator = WaveSyncOrchestrator(services)
    plan = orchestrator.get_execution_plan()

    print(f"✓ Total Services: {plan['graph_metrics']['total_services']}")
    print(f"✓ Total Dependencies: {plan['graph_metrics']['total_dependencies']}")
    print(f"✓ Critical Path Depth: {plan['graph_metrics']['critical_path_depth']}")

    print(f"\n✓ Execution Sequence (First 10):")
    for detail in plan['service_details'][:10]:
        print(f"  {detail['sequence_position']:2d}. {detail['service_id']:30s} "
              f"(Priority: {detail['priority']}, Score: {detail['score']:5.2f}, "
              f"Out-Degree: {detail['out_degree']})")

    print(f"\n✓ ... [Services 11-15] ...")
    print(f"\n✓ Execution Sequence (Last 10):")
    for detail in plan['service_details'][-10:]:
        print(f"  {detail['sequence_position']:2d}. {detail['service_id']:30s} "
              f"(Priority: {detail['priority']}, Score: {detail['score']:5.2f}, "
              f"Out-Degree: {detail['out_degree']})")


def example_5_idempotent_resumption():
    """
    Example 5: Idempotent resumption after partial execution.
    Shows how to resume from a checkpoint.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Idempotent Resumption (Checkpoint Recovery)")
    print("=" * 70)

    services = [
        ServiceNode(id="db", priority=10, depends_on=[]),
        ServiceNode(id="cache", priority=9, depends_on=["db"]),
        ServiceNode(id="auth", priority=9, depends_on=["db"]),
        ServiceNode(id="api", priority=8, depends_on=["auth", "cache"]),
        ServiceNode(id="ui", priority=7, depends_on=["api"]),
    ]

    orchestrator = WaveSyncOrchestrator(services)
    full_sequence = orchestrator.get_serial_sequence()

    print(f"✓ Full Execution Sequence:")
    for idx, service_id in enumerate(full_sequence, 1):
        print(f"  {idx}. {service_id}")

    # Simulate first 3 services successfully executed
    executed = full_sequence[:3]
    print(f"\n✓ Checkpoint: First {len(executed)} services successfully executed: {executed}")

    # Resume from checkpoint
    remaining = orchestrator.is_idempotent(executed)
    print(f"✓ Remaining Services to Execute: {remaining}")


def example_6_determinism_check():
    """
    Example 6: Verify determinism.
    Runs the orchestrator multiple times with same input and verifies identical output.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Determinism Verification")
    print("=" * 70)

    def create_services():
        return [
            ServiceNode(id="svc-a", priority=5, depends_on=[]),
            ServiceNode(id="svc-b", priority=7, depends_on=["svc-a"]),
            ServiceNode(id="svc-c", priority=3, depends_on=[]),
            ServiceNode(id="svc-d", priority=9, depends_on=["svc-b", "svc-c"]),
            ServiceNode(id="svc-e", priority=6, depends_on=["svc-d"]),
        ]

    sequences = []
    for run in range(5):
        orch = WaveSyncOrchestrator(create_services())
        seq = orch.get_serial_sequence()
        sequences.append(seq)
        print(f"  Run {run + 1}: {seq}")

    # Verify all sequences are identical
    all_same = all(seq == sequences[0] for seq in sequences)
    print(f"\n✓ Determinism Check: {'PASSED ✓' if all_same else 'FAILED ✗'}")


def example_7_error_handling():
    """
    Example 7: Error handling and validation.
    Demonstrates how the engine handles invalid input.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Error Handling & Validation")
    print("=" * 70)

    from graph_engine import MigrationCycleError, InvalidServiceError

    # Test 1: Self-dependency detection
    print("\n  Test 1: Self-Dependency Detection")
    try:
        bad_service = ServiceNode(
            id="self-referential",
            priority=5,
            depends_on=["self-referential"]
        )
    except ValueError as e:
        print(f"    ✓ Caught Error: {e}")

    # Test 2: Circular dependency detection
    print("\n  Test 2: Circular Dependency Detection")
    try:
        services = [
            ServiceNode(id="svc-x", priority=5, depends_on=["svc-y"]),
            ServiceNode(id="svc-y", priority=5, depends_on=["svc-x"]),
        ]
        WaveSyncOrchestrator(services)
    except MigrationCycleError as e:
        print(f"    ✓ Caught Error: {e}")

    # Test 3: Missing dependency detection
    print("\n  Test 3: Missing Dependency Detection")
    try:
        services = [
            ServiceNode(id="svc-p", priority=5, depends_on=["non-existent"]),
        ]
        WaveSyncOrchestrator(services)
    except InvalidServiceError as e:
        print(f"    ✓ Caught Error: {e}")

    # Test 4: Duplicate ID detection
    print("\n  Test 4: Duplicate Service ID Detection")
    try:
        services = [
            ServiceNode(id="duplicate", priority=5, depends_on=[]),
            ServiceNode(id="duplicate", priority=5, depends_on=[]),
        ]
        WaveSyncOrchestrator(services)
    except InvalidServiceError as e:
        print(f"    ✓ Caught Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "*" * 70)
    print("WaveSync Graph & Logic Engine - Usage Examples")
    print("*" * 70)

    example_1_simple_chain()
    example_2_diamond_pattern()
    example_3_priority_optimization()
    example_4_complex_microservices()
    example_5_idempotent_resumption()
    example_6_determinism_check()
    example_7_error_handling()

    print("\n" + "*" * 70)
    print("All examples completed successfully! ✓")
    print("*" * 70 + "\n")


if __name__ == "__main__":
    main()

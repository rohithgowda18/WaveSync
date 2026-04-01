"""
Test suite for the WaveSync Graph & Logic Engine.
Validates all core functionality: DAG validation, cycle detection, and serial sequencing.
"""

import pytest
from typing import List

from wavesync.engine.models import ServiceNode
from wavesync.engine.orchestrator import WaveSyncOrchestrator
from wavesync.engine.exceptions import MigrationCycleError, InvalidServiceError


class TestServiceNodeValidation:
    """Test data validation for ServiceNode."""

    def test_valid_service_creation(self):
        """Test creation of a valid service node."""
        service = ServiceNode(
            id="auth-service",
            priority=9,
            depends_on=["database"],
            metadata={"owner": "security-team"},
        )
        assert service.id == "auth-service"
        assert service.priority == 9
        assert service.depends_on == ["database"]

    def test_self_dependency_rejected(self):
        """Test that a service cannot depend on itself."""
        with pytest.raises(ValueError, match="cannot depend on itself"):
            ServiceNode(
                id="auth-service",
                priority=9,
                depends_on=["auth-service"],  # Self-reference
            )

    def test_priority_bounds_validation(self):
        """Test that priority must be between 1 and 10."""
        with pytest.raises(ValueError):
            ServiceNode(id="service", priority=0)  # Too low

        with pytest.raises(ValueError):
            ServiceNode(id="service", priority=11)  # Too high

    def test_empty_dependency_string_rejected(self):
        """Test that empty strings are not allowed in depends_on."""
        with pytest.raises(ValueError, match="empty strings"):
            ServiceNode(
                id="service",
                priority=5,
                depends_on=["valid-dep", ""],  # Empty string
            )


class TestDAGValidation:
    """Test DAG validation and cycle detection."""

    def test_acyclic_graph_valid(self):
        """Test that a valid DAG is accepted."""
        services = [
            ServiceNode(id="db", priority=9, depends_on=[]),
            ServiceNode(id="cache", priority=8, depends_on=[]),
            ServiceNode(id="auth", priority=8, depends_on=["db"]),
            ServiceNode(id="api", priority=7, depends_on=["auth", "cache"]),
        ]
        # Should not raise
        orchestrator = WaveSyncOrchestrator(services)
        assert orchestrator.graph is not None

    def test_circular_dependency_detected(self):
        """Test that circular dependencies are detected."""
        services = [
            ServiceNode(id="service-a", priority=5, depends_on=["service-b"]),
            ServiceNode(id="service-b", priority=5, depends_on=["service-c"]),
            ServiceNode(id="service-c", priority=5, depends_on=["service-a"]),
        ]
        with pytest.raises(MigrationCycleError) as excinfo:
            WaveSyncOrchestrator(services)
        assert len(excinfo.value.cycle_services) > 0

    def test_two_node_cycle_detected(self):
        """Test detection of simple 2-node cycles."""
        services = [
            ServiceNode(id="service-a", priority=5, depends_on=["service-b"]),
            ServiceNode(id="service-b", priority=5, depends_on=["service-a"]),
        ]
        with pytest.raises(MigrationCycleError):
            WaveSyncOrchestrator(services)


class TestMigrationScoring:
    """Test the migration score calculation."""

    def test_migration_score_calculation(self):
        """Test that migration scores are calculated correctly."""
        services = [
            ServiceNode(id="db", priority=10, depends_on=[]),
            ServiceNode(id="cache", priority=5, depends_on=[]),
            ServiceNode(id="auth", priority=8, depends_on=["db"]),
            ServiceNode(id="api", priority=7, depends_on=["auth", "cache"]),
        ]
        orchestrator = WaveSyncOrchestrator(services)

        # DB has priority=10, out-degree=1 (auth depends on it)
        # Score = (10 * 0.7) + (1 * 0.3) = 7.0 + 0.3 = 7.3
        db_score = orchestrator._calculate_migration_score("db")
        assert db_score == 7.3

        # Cache has priority=5, out-degree=1 (api depends on it)
        # Score = (5 * 0.7) + (1 * 0.3) = 3.5 + 0.3 = 3.8
        cache_score = orchestrator._calculate_migration_score("cache")
        assert cache_score == 3.8

    def test_higher_priority_wins_same_out_degree(self):
        """Test that higher business priority wins when out-degree is the same."""
        services = [
            ServiceNode(id="high-pri", priority=10, depends_on=[]),
            ServiceNode(id="low-pri", priority=1, depends_on=[]),
            ServiceNode(id="consumer", priority=5, depends_on=["high-pri", "low-pri"]),
        ]
        orchestrator = WaveSyncOrchestrator(services)

        high_score = orchestrator._calculate_migration_score("high-pri")
        low_score = orchestrator._calculate_migration_score("low-pri")

        assert high_score > low_score

    def test_higher_out_degree_impacts_score(self):
        """Test that services with higher out-degree get higher scores."""
        services = [
            ServiceNode(id="critical", priority=5, depends_on=[]),
            ServiceNode(id="consumer1", priority=5, depends_on=["critical"]),
            ServiceNode(id="consumer2", priority=5, depends_on=["critical"]),
            ServiceNode(id="consumer3", priority=5, depends_on=["critical"]),
            ServiceNode(id="backup", priority=5, depends_on=[]),
        ]
        orchestrator = WaveSyncOrchestrator(services)

        critical_score = orchestrator._calculate_migration_score("critical")
        backup_score = orchestrator._calculate_migration_score("backup")

        # Critical has out-degree=3, backup has out-degree=0
        assert critical_score > backup_score


class TestSerialSequencing:
    """Test the serial sequence generation."""

    def test_respects_dependency_order(self):
        """Test that the sequence respects all dependencies."""
        services = [
            ServiceNode(id="db", priority=9, depends_on=[]),
            ServiceNode(id="cache", priority=8, depends_on=[]),
            ServiceNode(id="auth", priority=8, depends_on=["db"]),
            ServiceNode(id="api", priority=7, depends_on=["auth", "cache"]),
        ]
        orchestrator = WaveSyncOrchestrator(services)
        sequence = orchestrator.get_serial_sequence()

        # Dependencies must come before dependents
        assert sequence.index("db") < sequence.index("auth")
        assert sequence.index("cache") < sequence.index("api")
        assert sequence.index("auth") < sequence.index("api")

    def test_independent_services_ordered_by_score(self):
        """Test that independent services are ordered by migration score."""
        services = [
            ServiceNode(id="low-priority", priority=1, depends_on=[]),
            ServiceNode(id="high-priority", priority=10, depends_on=[]),
            ServiceNode(id="medium-priority", priority=5, depends_on=[]),
        ]
        orchestrator = WaveSyncOrchestrator(services)
        sequence = orchestrator.get_serial_sequence()

        # High priority should come before medium, which before low
        assert sequence.index("high-priority") < sequence.index("medium-priority")
        assert sequence.index("medium-priority") < sequence.index("low-priority")

    def test_deterministic_sequencing(self):
        """Test that running the algorithm twice produces the same result."""
        services = [
            ServiceNode(id="service-a", priority=5, depends_on=[]),
            ServiceNode(id="service-b", priority=7, depends_on=["service-a"]),
            ServiceNode(id="service-c", priority=3, depends_on=[]),
            ServiceNode(id="service-d", priority=9, depends_on=["service-c", "service-b"]),
        ]
        orchestrator = WaveSyncOrchestrator(services)

        sequence1 = orchestrator.get_serial_sequence()
        # Reset orchestrator and get sequence again
        orchestrator2 = WaveSyncOrchestrator(services)
        sequence2 = orchestrator2.get_serial_sequence()

        assert sequence1 == sequence2

    def test_all_services_in_sequence(self):
        """Test that all services appear exactly once in the sequence."""
        services = [
            ServiceNode(id=f"service-{i}", priority=(i % 9) + 1, depends_on=[])
            for i in range(25)  # Test with 25 services as per PRD
        ]
        orchestrator = WaveSyncOrchestrator(services)
        sequence = orchestrator.get_serial_sequence()

        assert len(sequence) == 25
        assert len(set(sequence)) == 25  # All unique


class TestIdempotency:
    """Test idempotent re-execution capabilities."""

    def test_idempotent_resumption(self):
        """Test that execution can resume from a partial sequence."""
        services = [
            ServiceNode(id="step-1", priority=1, depends_on=[]),
            ServiceNode(id="step-2", priority=2, depends_on=["step-1"]),
            ServiceNode(id="step-3", priority=3, depends_on=["step-2"]),
            ServiceNode(id="step-4", priority=4, depends_on=["step-3"]),
        ]
        orchestrator = WaveSyncOrchestrator(services)
        full_sequence = orchestrator.get_serial_sequence()

        # Simulate that first 2 services were executed
        executed = full_sequence[:2]
        remaining = orchestrator.is_idempotent(executed)

        # The remaining should be executable and maintain dependencies
        assert remaining == full_sequence[2:]


class TestExecutionPlan:
    """Test the execution plan generation."""

    def test_execution_plan_structure(self):
        """Test that execution plan has all required components."""
        services = [
            ServiceNode(id="db", priority=9, depends_on=[]),
            ServiceNode(id="auth", priority=8, depends_on=["db"]),
        ]
        orchestrator = WaveSyncOrchestrator(services)
        plan = orchestrator.get_execution_plan()

        assert "sequence_order" in plan
        assert "graph_metrics" in plan
        assert "service_details" in plan

        assert len(plan["sequence_order"]) == 2
        assert "critical_path_depth" in plan["graph_metrics"]

    def test_critical_path_calculation(self):
        """Test that critical path depth is calculated correctly."""
        # Linear dependency: a -> b -> c -> d
        services = [
            ServiceNode(id="a", priority=1, depends_on=[]),
            ServiceNode(id="b", priority=2, depends_on=["a"]),
            ServiceNode(id="c", priority=3, depends_on=["b"]),
            ServiceNode(id="d", priority=4, depends_on=["c"]),
        ]
        orchestrator = WaveSyncOrchestrator(services)
        plan = orchestrator.get_execution_plan()

        # Critical path is: a -> b -> c -> d (depth of 3 edges, 4 nodes)
        assert plan["graph_metrics"]["critical_path_depth"] == 4


class TestErrorHandling:
    """Test error handling and validation."""

    def test_missing_dependency_raises_error(self):
        """Test that referencing a non-existent dependency raises an error."""
        services = [
            ServiceNode(id="service-a", priority=5, depends_on=["non-existent"]),
        ]
        with pytest.raises(InvalidServiceError):
            WaveSyncOrchestrator(services)

    def test_duplicate_service_ids_rejected(self):
        """Test that duplicate service IDs are rejected."""
        services = [
            ServiceNode(id="service", priority=5, depends_on=[]),
            ServiceNode(id="service", priority=5, depends_on=[]),  # Duplicate
        ]
        with pytest.raises(InvalidServiceError):
            WaveSyncOrchestrator(services)

    def test_empty_services_list_rejected(self):
        """Test that an empty services list is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            WaveSyncOrchestrator([])


class TestComplexScenarios:
    """Test complex, real-world scenarios."""

    def test_large_service_set_50_services(self):
        """Test orchestration of 50 services as mentioned in PRD."""
        services = []
        for i in range(50):
            # Create pseudo-random dependencies
            depends_on = []
            if i > 0:
                depends_on.append(f"service-{i-1}")
            if i > 2:
                depends_on.append(f"service-{i-3}")

            services.append(
                ServiceNode(
                    id=f"service-{i}",
                    priority=(i % 10) + 1,
                    depends_on=depends_on,
                )
            )

        orchestrator = WaveSyncOrchestrator(services)
        sequence = orchestrator.get_serial_sequence()

        assert len(sequence) == 50
        assert len(set(sequence)) == 50

    def test_diamond_dependency_pattern(self):
        """Test the classic diamond dependency pattern."""
        # Pattern: bottom depends on two at level 1, both depend on top
        services = [
            ServiceNode(id="platform", priority=10, depends_on=[]),
            ServiceNode(id="auth", priority=8, depends_on=["platform"]),
            ServiceNode(id="cache", priority=8, depends_on=["platform"]),
            ServiceNode(id="api", priority=7, depends_on=["auth", "cache"]),
        ]
        orchestrator = WaveSyncOrchestrator(services)
        sequence = orchestrator.get_serial_sequence()

        # platform must come first
        assert sequence[0] == "platform"
        # api must come last
        assert sequence[-1] == "api"
        # auth and cache in middle in priority order
        assert sequence.index("auth") < sequence.index("api")
        assert sequence.index("cache") < sequence.index("api")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

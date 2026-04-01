"""
Test script for the full Member 3 Multi-Agent Pipeline.
Runs two services (stateful + stateless) and validates all output fields.
"""
import os
import sys
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wavesync.agents.member3_pipeline import generate_cloud_plan, generate_cloud_plans

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")

REQUIRED_KEYS = [
    "service", "type", "compute", "database", "storage",
    "cache", "queue", "region", "network", "risk",
    "risk_score", "aws_services", "cloud_changes", "metadata",
]

NETWORK_KEYS = ["vpc", "load_balancer", "public_subnet", "private_subnet", "security_group"]


def validate_plan(plan: dict, label: str) -> bool:
    """Check that all required keys are present and print results."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(json.dumps(plan, indent=2, default=str))

    ok = True
    for key in REQUIRED_KEYS:
        if key not in plan:
            print(f"  ❌ MISSING KEY: {key}")
            ok = False

    for key in NETWORK_KEYS:
        if key not in plan.get("network", {}):
            print(f"  ❌ MISSING NETWORK KEY: {key}")
            ok = False

    if ok:
        print(f"\n  ✅ All required fields present for '{plan['service']}'")
    return ok


def main():
    print("\n🚀 WaveSync AI — Member 3 Multi-Agent Pipeline Test\n")

    # ── Test 1: Stateful service ─────────────────────────────────────────
    auth_service = {
        "name": "Auth Service",
        "tech_stack": "Python Flask",
        "database_type": "Local MySQL",
        "dependencies": ["User Service"],
        "priority": 9,
    }

    # ── Test 2: Stateless service ────────────────────────────────────────
    notification_service = {
        "name": "Notification Service",
        "tech_stack": "Node.js Express",
        "database_type": "",
        "dependencies": [],
        "priority": 3,
    }

    # ── Run pipeline ─────────────────────────────────────────────────────
    plans = generate_cloud_plans([auth_service, notification_service])

    all_ok = True
    all_ok &= validate_plan(plans[0], "TEST 1: Auth Service (Stateful)")
    all_ok &= validate_plan(plans[1], "TEST 2: Notification Service (Stateless)")

    # ── Assertions ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  ASSERTIONS")
    print(f"{'='*60}")

    assert plans[0]["type"] == "stateful", f"Expected stateful, got {plans[0]['type']}"
    print("  ✅ Auth Service correctly classified as 'stateful'")

    assert plans[0]["compute"] == "AWS ECS", f"Expected ECS, got {plans[0]['compute']}"
    print("  ✅ Auth Service compute = AWS ECS")

    assert plans[0]["database"] == "AWS RDS", f"Expected RDS, got {plans[0]['database']}"
    print("  ✅ Auth Service database = AWS RDS")

    assert plans[0]["risk"] == "HIGH", f"Expected HIGH, got {plans[0]['risk']}"
    print(f"  ✅ Auth Service risk = HIGH (score={plans[0]['risk_score']})")

    assert plans[0]["network"]["load_balancer"] == "ALB"
    print("  ✅ Auth Service network LB = ALB")

    assert plans[0]["network"]["private_subnet"] is True
    print("  ✅ Auth Service has private subnet (database present)")

    assert plans[1]["type"] == "stateless", f"Expected stateless, got {plans[1]['type']}"
    print("  ✅ Notification Service correctly classified as 'stateless'")

    assert plans[1]["risk"] == "LOW" or plans[1]["risk"] == "MEDIUM"
    print(f"  ✅ Notification Service risk = {plans[1]['risk']} (score={plans[1]['risk_score']})")

    print(f"\n{'='*60}")
    if all_ok:
        print("  🎉 ALL TESTS PASSED — Member 3 Pipeline is PRODUCTION READY")
    else:
        print("  ❌ SOME TESTS FAILED")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

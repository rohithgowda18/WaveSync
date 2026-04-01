#!/usr/bin/env python
"""
WaveSync Topological Sort Demo
Demonstrates how microservices are ordered for deployment
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from wavesync.engine.kahn_priority_engine import PriorityExecutionEngine
from wavesync.deploy import get_microservice_info


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}".center(80))
    print("="*80)


def demo_topological_sort():
    """Demonstrate topological sort with example services"""
    
    print_section("🌊 WAVESYNC - TOPOLOGICAL SORT DEMO 🌊")
    
    # Example microservices with dependencies
    services_data = [
        {
            "id": "auth-service",
            "priority": 10,
            "depends_on": ["database"]
        },
        {
            "id": "database",
            "priority": 9,
            "depends_on": []
        },
        {
            "id": "user-service",
            "priority": 8,
            "depends_on": ["database", "auth-service"]
        },
        {
            "id": "api-gateway",
            "priority": 7,
            "depends_on": ["auth-service", "user-service"]
        },
        {
            "id": "payment-service",
            "priority": 6,
            "depends_on": ["database", "user-service"]
        },
        {
            "id": "notification-service",
            "priority": 5,
            "depends_on": ["messaging-queue"]
        },
        {
            "id": "messaging-queue",
            "priority": 4,
            "depends_on": ["database"]
        },
        {
            "id": "analytics-service",
            "priority": 3,
            "depends_on": ["database", "messaging-queue"]
        },
    ]
    
    print("\n📋 INPUT SERVICES (with dependencies):\n")
    for svc in services_data:
        deps = ", ".join(svc["depends_on"]) if svc["depends_on"] else "None"
        print(f"  • {svc['id']:25} | Priority: {svc['priority']} | Depends on: {deps}")
    
    # Execute Kahn's algorithm
    print_section("🔄 KAHN'S ALGORITHM - TOPOLOGICAL SORT")
    
    try:
        engine = PriorityExecutionEngine(services_data)
        topo_order = engine.execute()
        
        print("\n✅ Deployment Order (based on dependencies & priority):\n")
        
        for i, service_id in enumerate(topo_order, 1):
            info = get_microservice_info(service_id)
            
            # Find service in original data
            original = next(s for s in services_data if s["id"] == service_id)
            deps = ", ".join(original["depends_on"]) if original["depends_on"] else "None"
            
            print(f"\n  {i}️⃣  SERVICE: {service_id}")
            print(f"     └─ Type: {info['type']}")
            print(f"     └─ Reason: {info['reason']}")
            print(f"     └─ Priority Score: {original['priority']}")
            print(f"     └─ Dependencies: {deps}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    # Summary
    print_section("📊 SUMMARY")
    
    print(f"""
Total Microservices:     {len(services_data)}
Deployment Order:        {len(topo_order)} (all scheduled)
Algorithm Used:          Kahn's Algorithm (Priority-Weighted DAG)

Key Benefits:
  ✅ Respects all dependencies
  ✅ Maximizes parallelism where possible
  ✅ Prioritizes critical services first
  ✅ Guarantees acyclic ordering (no circular dependencies)
    """)
    
    print("="*80)


if __name__ == "__main__":
    demo_topological_sort()

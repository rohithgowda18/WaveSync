import os
import json
import time

from wavesync.engine.models import ServiceNode
from wavesync.engine.orchestrator import WaveSyncOrchestrator
from wavesync.agents.member3_pipeline import generate_cloud_plan

# Self-contained set of 25 enterprise-grade, realistic inter-dependent microservices
services_data = [
    {"name": "postgresql-main", "tech_stack": "PostgreSQL 14", "database": "postgresql", "dependencies": [], "priority": 1},
    {"name": "redis-cache", "tech_stack": "Redis 6", "database": "redis", "dependencies": [], "priority": 2},
    {"name": "auth-service", "tech_stack": "Node.js, Express", "database": "None", "dependencies": ["postgresql-main", "redis-cache"], "priority": 3},
    {"name": "user-service", "tech_stack": "Java Spring Boot", "database": "None", "dependencies": ["postgresql-main", "auth-service"], "priority": 4},
    {"name": "payment-gateway", "tech_stack": "Python FastAPI", "database": "None", "dependencies": ["auth-service"], "priority": 5},
    {"name": "order-service", "tech_stack": "Java Spring Boot", "database": "None", "dependencies": ["postgresql-main", "user-service", "payment-gateway"], "priority": 6},
    {"name": "inventory-db", "tech_stack": "MySQL", "database": "mysql", "dependencies": [], "priority": 1},
    {"name": "inventory-service", "tech_stack": "Go", "database": "None", "dependencies": ["inventory-db", "auth-service"], "priority": 7},
    {"name": "shipping-service", "tech_stack": "Node.js", "database": "None", "dependencies": ["order-service", "inventory-service"], "priority": 8},
    {"name": "email-notification-queue", "tech_stack": "RabbitMQ", "database": "None", "dependencies": [], "priority": 2},
    {"name": "notification-service", "tech_stack": "Python Celery", "database": "None", "dependencies": ["email-notification-queue", "user-service"], "priority": 9},
    {"name": "search-db", "tech_stack": "Elasticsearch", "database": "elasticsearch", "dependencies": [], "priority": 2},
    {"name": "catalog-indexer", "tech_stack": "Python worker", "database": "None", "dependencies": ["inventory-service", "search-db"], "priority": 8},
    {"name": "search-api", "tech_stack": "Go", "database": "None", "dependencies": ["search-db"], "priority": 7},
    {"name": "content-cdn", "tech_stack": "Local Nginx static files", "database": "None", "dependencies": [], "priority": 3},
    {"name": "recommendation-ml-engine", "tech_stack": "Python TensorFlow", "database": "None", "dependencies": ["user-service", "order-service"], "priority": 10},
    {"name": "analytics-db", "tech_stack": "ClickHouse", "database": "clickhouse", "dependencies": [], "priority": 2},
    {"name": "analytics-consumer", "tech_stack": "Kafka Consumer, Java", "database": "None", "dependencies": ["analytics-db", "order-service"], "priority": 10},
    {"name": "admin-dashboard", "tech_stack": "React SPA", "database": "None", "dependencies": ["auth-service", "analytics-db"], "priority": 8},
    {"name": "customer-support-db", "tech_stack": "MongoDB", "database": "mongodb", "dependencies": [], "priority": 1},
    {"name": "ticket-service", "tech_stack": "Node.js", "database": "None", "dependencies": ["customer-support-db", "auth-service"], "priority": 5},
    {"name": "chatbot-backend", "tech_stack": "Python LLM", "database": "None", "dependencies": ["ticket-service", "redis-cache"], "priority": 6},
    {"name": "billing-cron-job", "tech_stack": "Linux crontab bash scripts", "database": "None", "dependencies": ["payment-gateway"], "priority": 4},
    {"name": "fraud-detection-engine", "tech_stack": "Go", "database": "None", "dependencies": ["payment-gateway", "user-service"], "priority": 3},
    {"name": "api-gateway", "tech_stack": "Kong", "database": "None", "dependencies": ["auth-service", "user-service", "order-service", "search-api"], "priority": 2}
]

def run_viva_simulation():
    # 1. Dynamically write it back to a separate folder as requested by user
    mock_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(mock_dir, exist_ok=True)
    with open(os.path.join(mock_dir, "25_microservices.json"), "w") as f:
        json.dump(services_data, f, indent=4)

    print("\n" + "="*60)
    print("🚀 WAVESYNC AI: FULL PIPELINE MIGRATION SIMULATION")
    print("="*60 + "\n")
    print("✅ Created and saved 25 interconnected microservices inside 'data/25_microservices.json'")

    # 2. INSTANTIATE GRAPH ENGINE MEMORY
    service_nodes = []
    for s in services_data:
        service_nodes.append(ServiceNode(
            id=s["name"],
            priority=s["priority"],
            depends_on=s["dependencies"],
            metadata={"tech_stack": s["tech_stack"], "database_type": s["database"]}
        ))

    print("✅ Directed Acyclic Graph Topology mapped safely into memory.\n")

    # 3. RUN TOPOLOGICAL ENGINE
    print("⚙️ Initiating Modified Kahn's Priority-Weighted Sort...")
    orchestrator = WaveSyncOrchestrator(service_nodes)
    orchestrator.validate_dag() # Instant circular-tie break validation natively
    
    plan = orchestrator.get_execution_plan()
    execution_order = plan["sequence_order"]
    
    print(f"\n✅ DAG Sorted Successfully. No Cycles Detected.")
    print(f"📊 Matrix Size: {plan['graph_metrics']['total_services']} Services, {plan['graph_metrics']['total_dependencies']} Dependencies")
    print("\n--- EXPLICIT EXECUTION QUEUE ---")
    for i, _id in enumerate(execution_order):
        print(f" {i+1}. {_id}")
    
    print("\n" + "="*60)
    print("🤖 ENGAGING GROQ LLM: AWS CLOUD RECTIFICATION (1 at a time natively)")
    print("="*60 + "\n")

    ordered_payloads = []
    for ex_id in execution_order:
        match = next(s for s in services_data if s["name"] == ex_id)
        ordered_payloads.append(match)

    successes = 0
    print(f"Simulation Limits: Processing Top 3 Core Architectures directly to Groq Cloud...")
    
    for i, payload in enumerate(ordered_payloads[:3]):
        # Ensure payload has the correct keys for the pipeline
        payload["database_type"] = payload.get("database", "None")
        
        print(f"\n[{i+1}/3] 🧠 Generating Cloud Plan for `{payload['name']}` ({payload['tech_stack']})...")
        try:
            plan = generate_cloud_plan(payload)
            print(f"  ↳ TYPE:       {plan['type'].upper()} ({plan['classification_reason']})")
            print(f"  ↳ COMPUTE:    {plan['compute']} in {plan['region']}")
            print(f"  ↳ STACK:      {plan['database']}, {plan['storage']}, {plan['cache']}, {plan['queue']}")
            print(f"  ↳ NETWORK:    VPC={plan['network']['vpc']}, Public={plan['network']['public_subnet']}, Private={plan['network']['private_subnet']}")
            print(f"  ↳ RISK:       {plan['risk'].upper()} (Score: {plan['risk_score']})")
            successes += 1
        except Exception as e:
            print(f"  ↳ ❌ PIPELINE ERROR: {str(e)}")
            break
            
    # 4. GENERATE FINAL REPORT
    print("\n" + "="*60)
    print("📋 MIGRATION SIMULATION COMPLETE")
    print(f"Successfully Orchestrated Graph for: 25 Services")
    print(f"Successfully LLM-Rectified to AWS: {successes} Services")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_viva_simulation()

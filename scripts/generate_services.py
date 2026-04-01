"""
WaveSync AI — Service Generator
Utility to generate dummy microservice manifests for simulation.
"""

import json
import os

def generate_mock_services(count: int = 25, output_file: str = "data/25_microservices.json"):
    """
    Generates a set of interconnected microservices. 
    In a real scenario, this would be replaced by actual ingestion logic.
    """
    services = [
        {"name": "postgresql-main", "tech_stack": "PostgreSQL 14", "database": "postgresql", "dependencies": [], "priority": 1},
        {"name": "redis-cache", "tech_stack": "Redis 6", "database": "redis", "dependencies": [], "priority": 2},
        {"name": "auth-service", "tech_stack": "Node.js, Express", "database": "None", "dependencies": ["postgresql-main", "redis-cache"], "priority": 3},
        {"name": "user-service", "tech_stack": "Java Spring Boot", "database": "None", "dependencies": ["postgresql-main", "auth-service"], "priority": 4},
        # ... shortened for brevity in this script placeholder ...
    ]
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(services, f, indent=4)
    print(f"✅ Generated {len(services)} services in {output_file}")

if __name__ == "__main__":
    generate_mock_services()

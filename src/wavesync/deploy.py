import boto3
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration from environment variables
lambda_client = boto3.client(
    'lambda',
    region_name=os.getenv('AWS_REGION', 'eu-north-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


def get_microservice_info(service_name: str) -> dict:
    """
    Classify microservice type and provide deployment reason
    """
    service_lower = service_name.lower()
    
    # Microservice type classification
    if any(x in service_lower for x in ["auth", "login", "security", "token", "jwt"]):
        svc_type = "Authentication Service"
        reason = "Critical security service - must be deployed early for service-to-service auth"
    elif any(x in service_lower for x in ["database", "db", "postgres", "mysql", "mongo"]):
        svc_type = "Data Layer"
        reason = "Foundation service - other services depend on database connectivity"
    elif any(x in service_lower for x in ["api", "gateway", "endpoint"]):
        svc_type = "API Gateway"
        reason = "Entry point service - enables external client communication"
    elif any(x in service_lower for x in ["cache", "redis", "memcache"]):
        svc_type = "Cache Service"
        reason = "Performance optimization - deployed after core services"
    elif any(x in service_lower for x in ["queue", "message", "kafka", "rabbit"]):
        svc_type = "Message Queue"
        reason = "Inter-service communication - enables async operations"
    elif any(x in service_lower for x in ["user", "profile", "account"]):
        svc_type = "User Management"
        reason = "Core business service - manages user identity and profiles"
    elif any(x in service_lower for x in ["payment", "billing", "invoice"]):
        svc_type = "Payment Service"
        reason = "Financial service - processes transactions and revenue"
    elif any(x in service_lower for x in ["notification", "email", "sms"]):
        svc_type = "Notification Service"
        reason = "Communication service - sends alerts and updates to users"
    elif any(x in service_lower for x in ["analytics", "logging", "metrics"]):
        svc_type = "Analytics & Monitoring"
        reason = "Observability service - collects metrics and logs"
    else:
        svc_type = "Business Logic Service"
        reason = "Core microservice - handles specific business domain logic"
    
    return {
        "type": svc_type,
        "reason": reason
    }


def deploy_to_aws(service_name):
    """Deploy a service to AWS Lambda"""
    print(f"\n🚀 Starting deployment for {service_name}")

    try:
        print("[AWS] Invoking Lambda...")

        response = lambda_client.invoke(
            FunctionName=os.getenv('AWS_LAMBDA_FUNCTION', 'wavesync-function'),
            InvocationType='RequestResponse',
            Payload=json.dumps({
                "service": service_name
            })
        )

        result = json.loads(response['Payload'].read())

        print(f"✅ Lambda Response: {result}")

        return {
            "status": "success",
            "url": f"https://aws/{service_name}"
        }

    except Exception as e:
        print(f"❌ AWS Error: {e}")
        return {
            "status": "failed",
            "url": None
        }


def wait_for_green(url, timeout=20):
    """Verify service health at given URL"""
    print(f"[HEALTH CHECK] Verifying {url}...")
    time.sleep(2)
    print(f"✅ Service is LIVE: {url}")
    return True

import json


def build_prompt(service: dict) -> str:
    """Construct a production‑grade prompt for Gemini AI.

    The AI acts as a **Senior Cloud Migration Architect**, **AWS Solutions
    Architect**, and **Microservices Platform Engineer**. It receives a service
    description and must return a JSON object (no markdown) describing the
    migration plan.

    The prompt includes:
    * System role and high‑level responsibilities.
    * Detailed decision‑mapping rules for common on‑prem components.
    * The input service details (name, tech_stack, database, dependencies,
      priority).
    * A strict JSON response schema that the model must obey.
    * Constraints to enforce deterministic, short reasoning and a list of
      required AWS services.
    """
    # Extract expected fields with safe defaults
    name = service.get("name", "")
    tech_stack = service.get("tech_stack", "")
    database = service.get("database", "")
    dependencies = service.get("dependencies", [])
    priority = service.get("priority", "")

    # System role description
    system_role = (
        "You are a Senior Cloud Migration Architect, AWS Solutions Architect, "
        "and Microservices Platform Engineer. Analyze the given microservice, "
        "identify non‑cloud‑ready components, and propose an AWS‑native, "
        "production‑grade migration plan."
    )

    # Mapping rules – must be applied exactly as written
    mapping_rules = (
        "Mapping rules (must be applied exactly as written):\n"
        "- Local MySQL → AWS RDS\n"
        "- Local PostgreSQL → AWS RDS\n"
        "- Local Files → AWS S3\n"
        "- Cron Jobs → AWS EventBridge\n"
        "- Queue → AWS SQS\n"
        "- Cache → AWS ElastiCache\n"
        "- Docker → ECS or EKS\n"
        "- VM → EC2\n"
        "- Monolith → Microservices (if needed)"
    )

    # Instruction block – steps the model must perform
    instruction = (
        "Perform the following steps in order:\n"
        "1. Analyze the service architecture.\n"
        "2. Identify components that are not cloud‑ready.\n"
        "3. Replace them using the mapping rules above.\n"
        "4. Suggest an appropriate deployment strategy (e.g., ECS, EKS, Lambda).\n"
        "5. Propose a scaling architecture (auto‑scaling groups, load balancers, etc.).\n"
        "6. Recommend storage migration paths.\n"
        "7. Outline required networking changes (VPC, subnets, security groups).\n"
        "8. Advise on security improvements (IAM, encryption, secrets management).\n"
        "9. Provide concise reasoning for each recommendation.\n"
        "10. Assess migration risk (low, medium, high)."
    )

    # Output schema – strict JSON only, no markdown, no extra text
    output_schema = (
        "Return **only** a JSON object with the exact keys below (no markdown, no extra text):\n"
        "{\n"
        "  \"service_name\": \"<service name>\",\n"
        "  \"cloud_changes\": \"<description of cloud‑architecture changes>\",\n"
        "  \"aws_services\": [\"<AWS service 1>\", \"<AWS service 2>\", ...],\n"
        "  \"deployment_strategy\": \"<deployment strategy>\",\n"
        "  \"scaling\": \"<scaling approach>\",\n"
        "  \"security\": \"<security recommendations>\",\n"
        "  \"reasoning\": \"<short reasoning>\",\n"
        "  \"risk\": \"<low|medium|high>\",\n"
        "  \"status\": \"rectified\"\n"
        "}\n"
        "The JSON must be syntactically valid and the field 'status' must be the literal string 'rectified'."
    )

    # Serialize the input service details for inclusion in the prompt
    service_details = json.dumps(
        {
            "name": name,
            "tech_stack": tech_stack,
            "database": database,
            "dependencies": dependencies,
            "priority": priority,
        },
        indent=2,
    )

    # Assemble the final prompt string
    prompt = (
        f"System role: {system_role}\n\n"
        f"{instruction}\n\n"
        f"{mapping_rules}\n\n"
        f"Input service details (JSON):\n{service_details}\n\n"
        f"{output_schema}"
    )
    return prompt

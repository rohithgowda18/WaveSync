"""
WaveSync AI — Network Architect Agent (Config-Driven)

Generates the network layout for an AWS-deployed microservice using rules
from config/network_rules.yaml.
"""

import logging
from typing import Any, Dict

from wavesync.utils.config_loader import load_network_rules

logger = logging.getLogger(__name__)

# Load network rules once at module import
_RULES = load_network_rules()


class NetworkArchitect:
    """Deterministic network topology generator for AWS deployments."""

    def generate_network(
        self,
        service: Dict[str, Any],
        aws_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the network layout from the AWS architecture plan.

        Args:
            service:  Original service metadata.
            aws_plan: Output from ``AWSArchitect.generate_architecture``.

        Returns:
            Dict with keys: vpc, load_balancer, public_subnet,
            private_subnet, security_group, api_gateway.
        """
        name = service.get("name", "Unknown")
        compute = aws_plan.get("compute", "")
        database = aws_plan.get("database", "None")
        
        # Get the classification-based rules
        # We need to know the service type, but aws_plan might not have it.
        # Downstream we might need to pass it or re-classify.
        # For now, let's assume we can infer from 'notes' or just pass it in.
        # In a real pipeline, we'd pass the type along.
        
        # Heuristic: if database is present and compute is ECS/RDS related.
        # But better to have the type. Let's look at how member3_pipeline calls this.
        
        # For simplicity in this config refactor, we'll try to find the type 
        # from the 'notes' or fallback to stateless.
        svc_type = "stateless"
        if "classified as stateful" in aws_plan.get("notes", ""):
            svc_type = "stateful"
        elif "classified as infrastructure" in aws_plan.get("notes", ""):
            svc_type = "infrastructure"
        elif "classified as data-service" in aws_plan.get("notes", ""):
            svc_type = "data-service"

        rules = _RULES.get(svc_type, _RULES.get("stateless", {}))

        # ── VPC & Security Group ─────────────────────────────────────────
        vpc = rules.get("vpc", True)
        security_group = rules.get("security_group", True)

        # ── Load Balancer ────────────────────────────────────────────────
        load_balancer = rules.get("load_balancer", "ALB")
        api_gateway = rules.get("api_gateway", False)

        # Override LB based on compute if needed (e.g. Lambda)
        if "Lambda" in compute:
            load_balancer = "None"
            api_gateway = True

        # ── Subnets ─────────────────────────────────────────────────────
        public_subnet = rules.get("public_subnet", True)
        
        # Private subnet: if rule says so, or if database is present
        private_subnet = rules.get("private_subnet", False)
        if database != "None":
             private_subnet = True

        network = {
            "vpc": vpc,
            "load_balancer": load_balancer,
            "public_subnet": public_subnet,
            "private_subnet": private_subnet,
            "security_group": security_group,
            "api_gateway": api_gateway,
        }

        logger.info(
            "Network layout for '%s': LB=%s, private_subnet=%s",
            name, load_balancer, private_subnet,
        )
        return network

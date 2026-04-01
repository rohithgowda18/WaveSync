"""
WaveSync AI — Member 3 Master Pipeline

Orchestrates all five specialised agents into a single, deterministic
execution flow that transforms a legacy service definition into a
comprehensive AWS cloud migration plan.

Pipeline Order:
    1. ServiceClassifier   → Determine service type
    2. Rectifier           → Map legacy components to AWS equivalents
    3. AWSArchitect        → Generate compute / database / storage plan
    4. NetworkArchitect    → Generate VPC / subnet / LB layout
    5. RiskAgent           → Calculate migration risk score

Usage:
    >>> from wavesync.agents.member3_pipeline import generate_cloud_plan
    >>> plan = generate_cloud_plan({"name": "Auth Service", ...})
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from wavesync.agents.service_classifier import ServiceClassifier
from wavesync.agents.rectifier import Rectifier
from wavesync.agents.aws_architect import AWSArchitect
from wavesync.agents.network_architect import NetworkArchitect
from wavesync.agents.risk_agent import RiskAgent

logger = logging.getLogger(__name__)

# ── Singleton agent instances (stateless, safe to reuse) ─────────────────────
_classifier = ServiceClassifier()
_rectifier = Rectifier()
_architect = AWSArchitect()
_network = NetworkArchitect()
_risk = RiskAgent()


def generate_cloud_plan(service: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the full Member 3 pipeline for a single *service*.

    Args:
        service: Service metadata dict with keys ``name``, ``tech_stack``,
                 ``database_type``, ``dependencies``, ``priority``.

    Returns:
        A unified cloud migration plan dictionary containing outputs from
        every agent in the pipeline.
    """
    start = time.time()
    name = service.get("name", "Unknown")
    logger.info("═══ Member 3 Pipeline START for '%s' ═══", name)

    # ── Stage 1: Classification ──────────────────────────────────────────
    logger.info("[1/5] Classifying service...")
    classification = _classifier.classify(service)
    service_type = classification["type"]

    # ── Stage 2: Rectification ───────────────────────────────────────────
    logger.info("[2/5] Rectifying legacy components...")
    rectification = _rectifier.rectify(service)

    # ── Stage 3: AWS Architecture ────────────────────────────────────────
    logger.info("[3/5] Generating AWS architecture...")
    aws_plan = _architect.generate_architecture(service, service_type=service_type)

    # ── Stage 4: Network Layout ──────────────────────────────────────────
    logger.info("[4/5] Generating network layout...")
    network = _network.generate_network(service, aws_plan)

    # ── Stage 5: Risk Assessment ─────────────────────────────────────────
    logger.info("[5/5] Calculating migration risk...")
    risk = _risk.assess_risk(service)

    # ── Assemble final plan ──────────────────────────────────────────────
    duration = time.time() - start
    plan = {
        "service": name,
        "type": service_type,
        "classification_reason": classification["reason"],
        "compute": aws_plan["compute"],
        "database": aws_plan["database"],
        "storage": aws_plan["storage"],
        "cache": aws_plan["cache"],
        "queue": aws_plan["queue"],
        "region": aws_plan["region"],
        "network": network,
        "risk": risk["risk"],
        "risk_score": risk["score"],
        "risk_breakdown": risk["breakdown"],
        "cloud_changes": rectification["cloud_changes"],
        "aws_services": rectification["aws_services"],
        "metadata": {
            "pipeline_version": "3.0.0",
            "duration_seconds": round(duration, 4),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    }

    logger.info(
        "═══ Member 3 Pipeline COMPLETE for '%s' — %s risk, %.2fs ═══",
        name, risk["risk"], duration,
    )
    return plan


def generate_cloud_plans(services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Batch-process a list of services through the Member 3 pipeline.

    Args:
        services: List of service metadata dicts.

    Returns:
        List of cloud migration plan dicts.
    """
    total = len(services)
    logger.info("Starting batch Member 3 pipeline for %d services", total)
    plans = []
    for idx, svc in enumerate(services, start=1):
        logger.info("Processing service %d/%d: %s", idx, total, svc.get("name", "?"))
        plans.append(generate_cloud_plan(svc))
    logger.info("Batch pipeline complete. %d plans generated.", total)
    return plans

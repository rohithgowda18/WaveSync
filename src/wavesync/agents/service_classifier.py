"""
WaveSync AI — Service Classifier Agent (Config-Driven)

Deterministic, rule-based classification of microservices into architectural
categories. This agent reads its keyword sets from config/classification_rules.yaml.

Categories:
    - stateful       : Service owns persistent data (database, file storage).
    - stateless      : Pure API / compute with no local persistence.
    - infrastructure : Supporting service (cache, queue, scheduler).
    - data-service   : Dedicated data pipeline or ETL workload.
"""

import logging
from typing import Any, Dict, Set

from wavesync.utils.config_loader import load_classification_rules

logger = logging.getLogger(__name__)

# Load classification rules once at module import
_RULES = load_classification_rules()
_DATABASE_KEYWORDS = set(_RULES.get("database_keywords", []))
_CACHE_KEYWORDS = set(_RULES.get("cache_keywords", []))
_QUEUE_KEYWORDS = set(_RULES.get("queue_keywords", []))
_DATA_KEYWORDS = set(_RULES.get("data_keywords", []))


class ServiceClassifier:
    """Classify a microservice into one of four canonical types.

    The classifier uses a strict priority waterfall:
        1. If the service has a database component  → ``stateful``
        2. If the service is a data/ETL workload    → ``data-service``
        3. If the service is cache- or queue-centric → ``infrastructure``
        4. Otherwise                                 → ``stateless``
    """

    def classify(self, service: Dict[str, Any]) -> Dict[str, str]:
        """Return ``{"type": "<category>", "reason": "<explanation>"}``.

        Args:
            service: Service metadata dict with keys like ``name``,
                     Tech_stack, ``database_type``, ``dependencies``.
        """
        name = service.get("name", "Unknown").lower()
        tech = service.get("tech_stack", "").lower()
        db = service.get("database_type", "").lower()
        deps = " ".join(service.get("dependencies", [])).lower()
        combined = f"{name} {tech} {db} {deps}"

        # ── Priority 1: Database present → stateful ──────────────────────
        if db and any(kw in db for kw in _DATABASE_KEYWORDS):
            reason = f"Uses database ({service.get('database_type', '')})"
            logger.info("Classified '%s' as stateful — %s", service.get("name"), reason)
            return {"type": "stateful", "reason": reason}

        # ── Priority 2: Data / ETL workload ──────────────────────────────
        if any(kw in combined for kw in _DATA_KEYWORDS):
            reason = "Identified as a data / ETL workload"
            logger.info("Classified '%s' as data-service — %s", service.get("name"), reason)
            return {"type": "data-service", "reason": reason}

        # ── Priority 3: Cache or queue → infrastructure ──────────────────
        if any(kw in combined for kw in _CACHE_KEYWORDS | _QUEUE_KEYWORDS):
            reason = "Cache or queue component detected"
            logger.info("Classified '%s' as infrastructure — %s", service.get("name"), reason)
            return {"type": "infrastructure", "reason": reason}

        # ── Priority 4: Default → stateless API ─────────────────────────
        reason = "No persistent state detected — treated as stateless API"
        logger.info("Classified '%s' as stateless — %s", service.get("name"), reason)
        return {"type": "stateless", "reason": reason}

"""
WaveSync AI — Risk Agent (Config-Driven)

Calculates the migration risk score for a microservice using a
deterministic, weighted formula with weights from config/risk_weights.yaml.
"""

import logging
from typing import Any, Dict

from wavesync.utils.config_loader import load_risk_weights

logger = logging.getLogger(__name__)

# Load risk weights once at module import
_CONFIG = load_risk_weights()
_WEIGHTS = _CONFIG.get("weights", {})
_THRESHOLDS = _CONFIG.get("thresholds", {})


class RiskAgent:
    """Deterministic migration risk calculator."""

    def assess_risk(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the migration risk score for a *service*.

        Args:
            service: Service metadata dict with ``name``, ``dependencies``,
                     ``database_type``, ``priority``.

        Returns:
            Dict with keys ``risk`` (LOW | MEDIUM | HIGH), ``score`` (int),
            and ``breakdown`` (dict with individual component scores).
        """
        name = service.get("name", "Unknown")

        # ── Weights (from YAML) ──────────────────────────────────────────
        dep_weight = _WEIGHTS.get("dependencies", 2)
        db_weight = _WEIGHTS.get("database", 3)
        pri_weight = _WEIGHTS.get("priority", 1)

        # ── Thresholds (from YAML) ───────────────────────────────────────
        high_threshold = _THRESHOLDS.get("high", 7)
        medium_threshold = _THRESHOLDS.get("medium", 4)

        # ── Component scores ─────────────────────────────────────────────
        num_deps = len(service.get("dependencies", []))
        dep_score = num_deps * dep_weight

        db_present = 1 if service.get("database_type", "") else 0
        db_score = db_present * db_weight

        priority = service.get("priority", 1)
        priority_score = priority * pri_weight

        # ── Total ────────────────────────────────────────────────────────
        total_score = dep_score + db_score + priority_score

        # ── Classification ───────────────────────────────────────────────
        if total_score >= high_threshold:
            risk_level = "HIGH"
        elif total_score >= medium_threshold:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        result = {
            "risk": risk_level,
            "score": total_score,
            "breakdown": {
                "dependencies": {"count": num_deps, "weighted": dep_score},
                "database": {"present": bool(db_present), "weighted": db_score},
                "priority": {"value": priority, "weighted": priority_score},
            },
        }

        logger.info(
            "Risk assessment for '%s': score=%d → %s", name, total_score, risk_level,
        )
        return result

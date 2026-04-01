"""
WaveSync AI — Rectifier Agent (Config-Driven)

Deterministic legacy-to-cloud mapping engine using rules from config/aws_mapping.yaml.
"""

import logging
from typing import Any, Dict, List

from wavesync.utils.config_loader import load_aws_mapping

logger = logging.getLogger(__name__)

# Load mapping once at module import
_AWS_MAPPING = load_aws_mapping()


class Rectifier:
    """Deterministic legacy-to-cloud mapping engine.

    Scans all text fields of a service definition against rules from
    aws_mapping.yaml and produces a structured change-set.
    """

    def rectify(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse *service* and return cloud transformation details.

        Args:
            service: Service metadata dict.

        Returns:
            Dict with keys ``cloud_changes`` (str) and ``aws_services`` (list).
        """
        name = service.get("name", "Unknown")
        tech = service.get("tech_stack", "").lower()
        db = service.get("database_type", "").lower()
        combined = f"{tech} {db}"

        matched_labels: List[str] = []
        matched_services: List[str] = []

        # We need a keyword-based mapping for the labels.
        # Let's derive it from the yaml mapping.
        
        for category, mappings in _AWS_MAPPING.items():
            if isinstance(mappings, dict):
                for keyword, aws_svc in mappings.items():
                    if keyword in combined:
                        label = f"{keyword.capitalize()} → {aws_svc}"
                        if label not in matched_labels:
                            matched_labels.append(label)
                        if aws_svc not in matched_services:
                            matched_services.append(aws_svc)

        # Always include default storage for logs/artifacts
        storage_map = _AWS_MAPPING.get("storage", {})
        default_storage = storage_map.get("local", "AWS S3")
        
        if default_storage not in matched_services:
            matched_services.append(default_storage)
            matched_labels.append(f"Log/Artifact Storage → {default_storage}")

        cloud_changes = "; ".join(matched_labels) if matched_labels else "No legacy components detected"

        logger.info("Rectified '%s': %d AWS services mapped", name, len(matched_services))
        return {
            "cloud_changes": cloud_changes,
            "aws_services": matched_services,
        }

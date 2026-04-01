"""
WaveSync AI — AWS Architect Agent (Config-Driven)

Deterministic mapper that reads all mapping rules from config/aws_mapping.yaml.
"""

import logging
from typing import Any, Dict

from wavesync.utils.config_loader import load_aws_mapping

logger = logging.getLogger(__name__)

# Load mapping once at module import
_MAPPING = load_aws_mapping()


class AWSArchitect:
    """Deterministic AWS compute and infrastructure mapper using external YAML config.

    The class reads mapping rules from ``config/aws_mapping.yaml`` which can be
    edited without changing code. All decisions are driven by these tables.
    """

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.mapping = _MAPPING

    def generate_architecture(
        self,
        service: Dict[str, Any],
        service_type: str = "stateless",
    ) -> Dict[str, Any]:
        """Generate an AWS architecture plan for a single service.

        Args:
            service: Service metadata.
            service_type: Classification from ServiceClassifier.
        Returns:
            Dict with keys: service, compute, database, storage, cache, queue,
            region, notes.
        """
        name = service.get("name", "Unknown")
        tech = service.get("tech_stack", "").lower()
        db = service.get("database_type", "").lower()

        compute = self._map_compute(tech, service_type)
        database = self._map_database(db)
        
        # Storage: map 'local' or just default to AWS S3
        storage_map = self.mapping.get("storage", {})
        storage = storage_map.get("local", "AWS S3")
        
        cache = self._map_cache(tech, db)
        queue = self._map_queue(tech, db)
        notes = self._generate_notes(name, compute, database, service_type)

        plan = {
            "service": name,
            "compute": compute,
            "database": database,
            "storage": storage,
            "cache": cache,
            "queue": queue,
            "region": self.region,
            "notes": notes,
        }
        logger.info("AWS architecture generated for %s: compute=%s, db=%s", name, compute, database)
        return plan

    # ---------------------------------------------------------------------
    # Helper methods that consult the loaded mapping tables
    # ---------------------------------------------------------------------
    def _map_compute(self, tech: str, service_type: str) -> str:
        compute_map = self.mapping.get("compute", {})
        # 1. Direct tech match
        for keyword, svc in compute_map.items():
            if keyword in tech:
                return svc
        # 2. Classification-based fallback
        if service_type in compute_map:
            return compute_map[service_type]
        # 3. Final default
        return compute_map.get("default", "AWS ECS")

    def _map_database(self, db: str) -> str:
        db_map = self.mapping.get("database", {})
        if not db:
            return "None"
        for keyword, svc in db_map.items():
            if keyword in db:
                return svc
        return "None"

    def _map_cache(self, tech: str, db: str) -> str:
        cache_map = self.mapping.get("cache", {})
        combined = f"{tech} {db}"
        for keyword, svc in cache_map.items():
            if keyword in combined:
                return svc
        return "None"

    def _map_queue(self, tech: str, db: str) -> str:
        queue_map = self.mapping.get("queue", {})
        combined = f"{tech} {db}"
        for keyword, svc in queue_map.items():
            if keyword in combined:
                return svc
        return "None"

    @staticmethod
    def _generate_notes(name: str, compute: str, database: str, svc_type: str) -> str:
        parts = [f"{name} mapped to {compute}"]
        if database != "None":
            parts.append(f"with {database} for persistence")
        parts.append(f"(classified as {svc_type})")
        return " ".join(parts)

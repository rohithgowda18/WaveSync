import time
import logging
from typing import List, Dict, Any

# Local import – assumes rectify.py is in the same package/directory
from wavesync.agents.rectify import rectify

# Configure a module‑level logger (applications can reconfigure as needed)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Constants controlling retry and rate‑limit behaviour
MAX_RETRIES = 3               # Number of attempts per service
RETRY_DELAY_SECONDS = 2       # Base delay between retries (exponential back‑off applied)
RATE_LIMIT_DELAY_SECONDS = 1  # Delay between successive service calls to avoid throttling


def _process_service(service: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to rectify a single *service* with retry logic.

    Returns the dictionary produced by :func:`rectify`. If all retries fail due to
    an unexpected exception, a safe fallback structure is returned (mirroring the
    ``DEFAULT_OUTPUT`` from ``rectify.py``) with the error captured in the
    ``metadata`` field.
    """
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            return rectify(service)
        except Exception as exc:  # pragma: no cover – defensive fallback
            logger.exception(
                "Rectify attempt %d for service %s failed: %s",
                attempt + 1,
                service.get("name", "<unknown>"),
                exc,
            )
            attempt += 1
            # Exponential back‑off: increase delay with each retry
            sleep_time = RETRY_DELAY_SECONDS * attempt
            logger.info("Sleeping %s seconds before retrying service %s", sleep_time, service.get("name", "<unknown>"))
            time.sleep(sleep_time)
    # All retries exhausted – construct a minimal fallback result
    logger.error("All retries exhausted for service %s; returning fallback.", service.get("name", "<unknown>"))
    fallback = {
        "service_name": service.get("name", ""),
        "cloud_changes": "",
        "aws_services": [],
        "deployment_strategy": "",
        "scaling": "",
        "security": "",
        "reasoning": "",
        "risk": "",
        "status": "failed",
        "metadata": {
            "duration_seconds": 0,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "error": "All retries failed",
        },
    }
    return fallback


def rectify_all(services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process a list of *services* through the rectification pipeline.

    The function iterates over the provided services, invoking ``rectify`` for each
    one while handling errors, applying per‑service retries, and respecting a
    configurable delay between calls to avoid rate‑limit issues. Progress is logged
    at INFO level. The function never aborts because of a single failure – all
    results (including fallbacks) are collected and returned.
    """
    total = len(services)
    results: List[Dict[str, Any]] = []
    logger.info("Starting batch rectification of %d services", total)

    for idx, service in enumerate(services, start=1):
        logger.info("Processing service %d/%d: %s", idx, total, service.get("name", "<unknown>"))
        result = _process_service(service)
        results.append(result)
        # Respect a short pause between distinct service calls to stay within API limits
        if idx < total:
            logger.debug("Sleeping %s seconds before next service", RATE_LIMIT_DELAY_SECONDS)
            time.sleep(RATE_LIMIT_DELAY_SECONDS)

    logger.info("Batch rectification completed. Processed %d services.", total)
    return results

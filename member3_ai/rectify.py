import time
import logging
from datetime import datetime
from typing import Dict, Any

# Import the helper modules using package‑relative imports
from .prompt import build_prompt
from .ai_agent import call_gemini
from .parser import parse_response

# Configure a module‑level logger (applications can override this configuration)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Default fallback structure – mirrors the schema expected from the LLM model
DEFAULT_OUTPUT = {
    "service_name": "",
    "cloud_changes": "",
    "aws_services": [],
    "deployment_strategy": "",
    "scaling": "",
    "security": "",
    "reasoning": "",
    "risk": "",
    "status": "failed",
    "metadata": {},
}


def _attach_metadata(result: Dict[str, Any], start_ts: float, error: str = None) -> Dict[str, Any]:
    """Enrich *result* with timing and optional error information.

    The function adds a ``metadata`` key containing:
    * ``duration_seconds`` – elapsed time since *start_ts*
    * ``timestamp`` – ISO‑8601 UTC time of completion
    * ``error`` – optional error message when the workflow fails
    """
    duration = time.time() - start_ts
    meta = {
        "duration_seconds": duration,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if error:
        meta["error"] = error
    result["metadata"] = meta
    return result


def rectify(service: dict) -> dict:
    """Run the full rectification pipeline for a *service* description.

    Steps:
    1. Build a LLM prompt using :func:`prompt.build_prompt`.
    2. Call the LLM model via :func:`ai_agent.call_gemini`.
    3. Parse the raw model output with :func:`parser.parse_response`.
    4. Attach timing/metadata and ensure a stable return structure.

    The function is defensive – any exception results in a fallback dictionary
    based on ``DEFAULT_OUTPUT`` and includes the error message in the metadata.
    """
    start_time = time.time()
    try:
        # 1. Build the prompt
        logger.info("Building LLM prompt for service %s", service.get("name", "<unknown>"))
        prompt_text = build_prompt(service)

        # 2. Call LLM
        logger.info("Calling LLM model")
        raw_response = call_gemini(prompt_text, service_name=service.get("name", "<unknown>"))

        # 3. Parse the response
        logger.info("Parsing LLM response")
        parsed = parse_response(raw_response)

        # 4. Ensure the service name is populated (service name mapping)
        if not parsed.get("service_name"):
            parsed["service_name"] = service.get("name", "")

        # 5. Attach metadata and return
        return _attach_metadata(parsed, start_time)
    except Exception as exc:  # pragma: no cover – defensive fallback
        logger.exception("Rectification pipeline failed: %s", exc)
        fallback = DEFAULT_OUTPUT.copy()
        fallback["service_name"] = service.get("name", "")
        return _attach_metadata(fallback, start_time, error=str(exc))

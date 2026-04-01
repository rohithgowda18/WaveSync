import re
import json
import logging
from typing import Dict, Any

# Configure basic logging (can be overridden by the application)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Default response structure used when parsing fails
DEFAULT_RESPONSE = {
    "service_name": "",
    "cloud_changes": "",
    "aws_services": [],
    "deployment_strategy": "",
    "scaling": "",
    "security": "",
    "reasoning": "",
    "risk": "",
    "status": "failed",
}


def _extract_json(text: str) -> str:
    """Extract the first JSON object from *text*.
    
    Tolerates surrounding text by finding the first '{' and the matching
    last '}'. This is more robust than a single regex for balanced braces.
    """
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace == -1 or last_brace == -1 or last_brace < first_brace:
        # Fallback to look for content inside markdown code fences
        fence_pattern = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)
        fence_match = fence_pattern.search(text)
        if fence_match:
            return fence_match.group(1)
        return ""
        
    return text[first_brace : last_brace + 1]


def parse_response(text: str) -> Dict[str, Any]:
    """Parse the AI response *text* and return a dictionary matching the
    expected schema.

    The function is defensive: it extracts a JSON block, attempts to decode it,
    validates required keys, and falls back to ``DEFAULT_RESPONSE`` if anything
    goes wrong. It never raises an exception – all errors are logged and the
    default structure is returned.
    """
    if not isinstance(text, str):
        logger.warning("parse_response received non‑string input; returning default.")
        return DEFAULT_RESPONSE.copy()

    json_str = _extract_json(text)
    if not json_str:
        logger.warning("No JSON object found in AI response; returning default.")
        return DEFAULT_RESPONSE.copy()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from AI response: {e}; returning default.")
        return DEFAULT_RESPONSE.copy()

    # Ensure all expected keys exist; missing keys get default values
    result = DEFAULT_RESPONSE.copy()
    for key in result:
        if key in data:
            result[key] = data[key]
    # If the model returned a different status, keep the original (could be "rectified")
    if "status" in data and data["status"] != "failed":
        result["status"] = data["status"]
    return result

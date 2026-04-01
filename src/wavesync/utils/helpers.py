"""
WaveSync AI — Helper Utilities
Common formatting and data manipulation helpers.
"""

import json
from typing import Any, Dict

def format_json(data: Dict[str, Any]) -> str:
    """Standard formatting for JSON outputs across the project."""
    return json.dumps(data, indent=4)

def sanitize_id(id_str: str) -> str:
    """Ensures service IDs are URL-safe and standard."""
    return id_str.lower().replace(" ", "-").replace("_", "-")

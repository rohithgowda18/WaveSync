"""
Utility functions to load YAML configuration files for Member 3 agents.
The loader caches the parsed content on first call to avoid repeated I/O.
"""
import os
import yaml
from typing import Any, Dict

# Base directory for configuration files (relative to project root)
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "config"))

# Simple in‑memory cache
_cache: Dict[str, Any] = {}


def _load_yaml(filename: str) -> Dict[str, Any]:
    """Load a YAML file from the config directory.

    Args:
        filename: Name of the YAML file (e.g., ``aws_mapping.yaml``).
    Returns:
        Parsed YAML content as a dictionary.
    """
    path = os.path.join(CONFIG_DIR, filename)
    if path in _cache:
        return _cache[path]
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    _cache[path] = data
    return data


def load_aws_mapping() -> Dict[str, Any]:
    """Return the AWS mapping configuration.
    """
    return _load_yaml("aws_mapping.yaml")


def load_risk_weights() -> Dict[str, int]:
    """Return the risk weight configuration.
    """
    return _load_yaml("risk_weights.yaml")


def load_network_rules() -> Dict[str, Any]:
    """Return the network rules configuration.
    """
    return _load_yaml("network_rules.yaml")


def load_classification_rules() -> Dict[str, Any]:
    """Return the classification keywords for ServiceClassifier.
    """
    return _load_yaml("classification_rules.yaml")

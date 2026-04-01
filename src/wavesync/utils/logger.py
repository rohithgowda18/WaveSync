"""
WaveSync AI — Logging Utility
Standardized logging configuration for all project components.
"""

import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a logger with a standard format."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        
    return logger

import os
import time
import logging
from typing import Any, Dict

from dotenv import load_dotenv, find_dotenv
from groq import Groq

# Load environment variables (searches for .env in parent directories)
load_dotenv(find_dotenv())
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment. Check your .env file.")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Import configuration (model name, retry settings, etc.)
from .config import (
    GROQ_MODEL,
    TEMPERATURE,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
    GLOBAL_RATE_LIMIT_DELAY,
)

# Initialise Groq client once
client = Groq(api_key=GROQ_API_KEY)


def _call_groq(prompt: str, service_name: str = "<unknown>") -> str:
    """Send *prompt* to the Groq model and return the raw text response.

    Features:
    * per‑call logging (service name, start/end)
    * retry logic with exponential back‑off
    * graceful handling of API errors
    * global rate‑limit delay between successful calls
    """
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            logger.info(f"[{service_name}] Groq call attempt {attempt + 1} – sending prompt.")
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "system", "content": "You are a senior cloud migration architect."},
                          {"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
            )
            text = response.choices[0].message.content.strip()
            logger.info(f"[{service_name}] Groq response received successfully.")
            time.sleep(GLOBAL_RATE_LIMIT_DELAY)
            return text
        except Exception as e:
            logger.exception(f"[{service_name}] Groq call failed: {e}. Retrying.")
            attempt += 1
            backoff = RETRY_DELAY_SECONDS * attempt
            logger.info(f"[{service_name}] Sleeping {backoff}s before retry #{attempt + 1}.")
            time.sleep(backoff)
    logger.error(f"[{service_name}] All {MAX_RETRIES} Groq attempts failed.")
    raise RuntimeError("Failed to obtain response from Groq after multiple retries.")

# Backward‑compatible wrapper used by the rest of the codebase
def call_gemini(prompt: str, service_name: str = "<unknown>") -> str:
    """Alias kept for compatibility – forwards to Groq implementation."""
    return _call_groq(prompt, service_name)

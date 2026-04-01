# config.py – centralised configuration for the Member 3 AI agent

# Model settings
MODEL_NAME = "gemini-2.0-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.0          # deterministic output
MAX_OUTPUT_TOKENS = 2048

# Retry / back‑off settings
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2   # base delay; exponential back‑off applied in ai_agent.py

# Request timeout (seconds)
TIMEOUT_SECONDS = 30

# Global rate‑limit protection (delay between successful calls)
GLOBAL_RATE_LIMIT_DELAY = 1

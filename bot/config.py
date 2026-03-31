import os

# Telegram
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"].strip()

# AI provider
AI_API_KEY  = os.environ["AI_API_KEY"].strip()
AI_BASE_URL = os.environ.get("AI_BASE_URL", "https://api.cerebras.ai/v1").strip()
MODEL       = os.environ.get("AI_MODEL", "llama3.1-8b").strip()

# Redis
UPSTASH_URL   = os.environ["UPSTASH_REDIS_REST_URL"].strip()
UPSTASH_TOKEN = os.environ["UPSTASH_REDIS_REST_TOKEN"].strip()

# App
SYSTEM_PROMPT = (
    "You are a knowledgeable and concise AI assistant. "
    "Answer clearly and directly. Avoid unnecessary filler. "
    "If you are unsure about something, say so rather than guessing. "
    "Keep responses appropriately brief for a chat interface."
)
MAX_HISTORY = 20    # messages kept per user (10 conversation turns)
RATE_LIMIT  = int(os.environ.get("RATE_LIMIT", "50"))  # max messages per user per day
MAX_MSG_LEN = 4096  # Telegram's character limit per message

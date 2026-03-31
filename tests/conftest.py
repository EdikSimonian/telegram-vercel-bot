"""
Mocks all external dependencies before any bot module is imported.
This lets tests run without real API keys or network connections.
"""
import os
import sys
from unittest.mock import MagicMock

# ── Fake environment variables ─────────────────────────────────────────────────
os.environ["TELEGRAM_BOT_TOKEN"] = "1234567890:fake_token"
os.environ["AI_API_KEY"]         = "fake_api_key"
os.environ["UPSTASH_REDIS_REST_URL"]   = "https://fake.upstash.io"
os.environ["UPSTASH_REDIS_REST_TOKEN"] = "fake_redis_token"

# ── Mock external packages ─────────────────────────────────────────────────────
mock_bot_instance = MagicMock()
mock_bot_instance.get_me.return_value = MagicMock(id=42, username="testbot")

mock_telebot = MagicMock()
mock_telebot.TeleBot.return_value = mock_bot_instance

sys.modules["telebot"]       = mock_telebot
sys.modules["telebot.types"] = MagicMock()
sys.modules["openai"]        = MagicMock()
sys.modules["upstash_redis"] = MagicMock()
sys.modules["flask"]         = MagicMock()

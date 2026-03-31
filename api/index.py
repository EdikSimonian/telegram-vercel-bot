import os
import json
from datetime import date
from flask import Flask, request
import telebot
from openai import OpenAI
from upstash_redis import Redis

# ── Configuration ──────────────────────────────────────────────────────────────
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

# ── Clients ────────────────────────────────────────────────────────────────────
bot      = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
ai       = OpenAI(base_url=AI_BASE_URL, api_key=AI_API_KEY)
redis    = Redis(url=UPSTASH_URL, token=UPSTASH_TOKEN)
app      = Flask(__name__)
BOT_INFO = bot.get_me()  # cached at startup for group mention detection

# ── History helpers ────────────────────────────────────────────────────────────
def get_history(user_id: int) -> list:
    data = redis.get(f"chat:{user_id}")
    return json.loads(data) if data else []

def save_history(user_id: int, history: list) -> None:
    redis.set(f"chat:{user_id}", json.dumps(history[-MAX_HISTORY:]))

def clear_history(user_id: int) -> None:
    redis.delete(f"chat:{user_id}")

# ── Rate limiting ──────────────────────────────────────────────────────────────
def is_rate_limited(user_id: int) -> bool:
    key = f"rate:{user_id}:{date.today()}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, 86400)  # reset after 24 hours
    return count > RATE_LIMIT

# ── AI ─────────────────────────────────────────────────────────────────────────
def ask_ai(user_id: int, user_message: str) -> str:
    history = get_history(user_id)
    history.append({"role": "user", "content": user_message})

    response = ai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
    )

    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    save_history(user_id, history)
    return reply

# ── Helpers ────────────────────────────────────────────────────────────────────
def send_reply(message, text: str) -> None:
    """Split and send reply in chunks if over Telegram's 4096 char limit."""
    for i in range(0, len(text), MAX_MSG_LEN):
        bot.reply_to(message, text[i:i + MAX_MSG_LEN])

def should_respond(message) -> bool:
    """In groups, only respond when mentioned or replied to."""
    if message.chat.type == "private":
        return True
    if message.reply_to_message and message.reply_to_message.from_user.id == BOT_INFO.id:
        return True
    if message.text and f"@{BOT_INFO.username}" in message.text:
        return True
    return False

# ── Commands ───────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.reply_to(message, "Hello! I'm your AI assistant. Send me a message to get started.\n\nUse /help to see available commands.")

@bot.message_handler(commands=["help"])
def cmd_help(message):
    bot.reply_to(message,
        "/start — welcome message\n"
        "/help  — show this message\n"
        "/reset — clear conversation history\n"
        "/about — about this bot"
    )

@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    clear_history(message.from_user.id)
    bot.reply_to(message, "Conversation cleared. Starting fresh!")

@bot.message_handler(commands=["about"])
def cmd_about(message):
    bot.reply_to(message, f"Model  : {MODEL}\nStorage: Upstash Redis\nHosting: Vercel")

# ── Message handler ────────────────────────────────────────────────────────────
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if not should_respond(message):
        return
    if is_rate_limited(message.from_user.id):
        bot.reply_to(message, f"You've reached the daily limit of {RATE_LIMIT} messages. Try again tomorrow.")
        return
    bot.send_chat_action(message.chat.id, "typing")
    # Strip bot mention from group messages before sending to AI
    text = message.text.replace(f"@{BOT_INFO.username}", "").strip()
    try:
        reply = ask_ai(message.from_user.id, text)
        send_reply(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, f"Error: {e}")

# ── Webhook ────────────────────────────────────────────────────────────────────
@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data(as_text=True))
    bot.process_new_updates([update])
    return "OK", 200

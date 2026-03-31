import json
from bot.clients import redis
from bot.config import MAX_HISTORY


def get_history(user_id: int) -> list:
    data = redis.get(f"chat:{user_id}")
    return json.loads(data) if data else []


def save_history(user_id: int, history: list) -> None:
    redis.set(f"chat:{user_id}", json.dumps(history[-MAX_HISTORY:]))


def clear_history(user_id: int) -> None:
    redis.delete(f"chat:{user_id}")

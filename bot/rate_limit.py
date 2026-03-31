from datetime import date
from bot.clients import redis
from bot.config import RATE_LIMIT


def is_rate_limited(user_id: int) -> bool:
    key = f"rate:{user_id}:{date.today()}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, 86400)  # reset after 24 hours
    return count > RATE_LIMIT

from unittest.mock import patch


def test_first_message_not_limited():
    with patch("bot.rate_limit.redis") as mock_redis:
        with patch("bot.rate_limit.RATE_LIMIT", 50):
            mock_redis.incr.return_value = 1
            from bot.rate_limit import is_rate_limited
            assert is_rate_limited(123) is False


def test_message_at_limit_not_limited():
    with patch("bot.rate_limit.redis") as mock_redis:
        with patch("bot.rate_limit.RATE_LIMIT", 50):
            mock_redis.incr.return_value = 50
            from bot.rate_limit import is_rate_limited
            assert is_rate_limited(123) is False


def test_message_over_limit_is_limited():
    with patch("bot.rate_limit.redis") as mock_redis:
        with patch("bot.rate_limit.RATE_LIMIT", 50):
            mock_redis.incr.return_value = 51
            from bot.rate_limit import is_rate_limited
            assert is_rate_limited(123) is True


def test_sets_expiry_on_first_use():
    with patch("bot.rate_limit.redis") as mock_redis:
        mock_redis.incr.return_value = 1
        from bot.rate_limit import is_rate_limited
        is_rate_limited(123)
        mock_redis.expire.assert_called_once()

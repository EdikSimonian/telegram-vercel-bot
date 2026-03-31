import json
from unittest.mock import patch, MagicMock


def test_get_history_empty():
    with patch("bot.history.redis") as mock_redis:
        mock_redis.get.return_value = None
        from bot.history import get_history
        assert get_history(123) == []


def test_get_history_returns_parsed_data():
    history = [{"role": "user", "content": "Hello"}]
    with patch("bot.history.redis") as mock_redis:
        mock_redis.get.return_value = json.dumps(history)
        from bot.history import get_history
        assert get_history(123) == history


def test_save_history_trims_to_max():
    with patch("bot.history.redis") as mock_redis:
        with patch("bot.history.MAX_HISTORY", 2):
            from bot.history import save_history
            long_history = [{"role": "user", "content": str(i)} for i in range(10)]
            save_history(123, long_history)
            saved = json.loads(mock_redis.set.call_args[0][1])
            assert len(saved) == 2
            assert saved[-1]["content"] == "9"


def test_clear_history():
    with patch("bot.history.redis") as mock_redis:
        from bot.history import clear_history
        clear_history(123)
        mock_redis.delete.assert_called_once_with("chat:123")

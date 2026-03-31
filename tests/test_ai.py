from bot.ai import needs_search


def test_needs_search_detects_news():
    assert needs_search("what is the latest news about Iran?") is True


def test_needs_search_detects_today():
    assert needs_search("what happened today?") is True


def test_needs_search_detects_current():
    assert needs_search("who is the current president?") is True


def test_needs_search_false_for_general_question():
    assert needs_search("what is the capital of France?") is False


def test_needs_search_false_for_coding_question():
    assert needs_search("how do I reverse a list in Python?") is False


def test_needs_search_case_insensitive():
    assert needs_search("What is TODAY's weather?") is True

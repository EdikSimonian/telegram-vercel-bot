from bot.clients import ai
from bot.config import MODEL, SYSTEM_PROMPT, TAVILY_API_KEY
from bot.history import get_history, save_history

# Keywords that suggest the query needs current/real-time information
SEARCH_TRIGGERS = [
    "today", "latest", "current", "news", "now", "recent", "this week",
    "this month", "this year", "happened", "who won", "what is happening",
    "weather", "price", "score", "update", "announce", "release",
]


def needs_search(text: str) -> bool:
    text_lower = text.lower()
    return any(trigger in text_lower for trigger in SEARCH_TRIGGERS)


def ask_ai(user_id: int, user_message: str) -> str:
    history = get_history(user_id)
    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject search results when the query needs current information
    if TAVILY_API_KEY and needs_search(user_message):
        try:
            from bot.search import web_search
            results = web_search(user_message)
            messages.append({
                "role": "system",
                "content": f"Web search results for context:\n\n{results}",
            })
        except Exception as e:
            print(f"Search error: {e}")

    messages += history

    response = ai.chat.completions.create(model=MODEL, messages=messages)
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    save_history(user_id, history)
    return reply

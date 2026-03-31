from bot.clients import ai
from bot.config import MODEL, SYSTEM_PROMPT
from bot.history import get_history, save_history


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

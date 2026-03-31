import telebot
from flask import Flask, request
import bot.handlers  # registers all handlers with the bot
from bot.clients import bot

app = Flask(__name__)


@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data(as_text=True))
    bot.process_new_updates([update])
    return "OK", 200

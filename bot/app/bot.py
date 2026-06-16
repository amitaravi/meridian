import os

from telegram.ext import Application


def create_application() -> Application:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    return Application.builder().token(token).build()

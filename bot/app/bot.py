import os

from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from app.handlers.callbacks import handle_callback
from app.handlers.start import handle_start


def create_application() -> Application:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app

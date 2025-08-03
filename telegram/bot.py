import os

from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler

from common.config.config import TELEGRAM_BOT_TOKEN


class TelegramBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(CommandHandler('help', self.help_command))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hi! I'm trabajito, your job finder buddy! To start, I need to know what you are looking for, use the command /start to begin")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Available commands: \n/start - Configure your job seeking\n/help - Get info")

    def run(self):
        self.app.run_polling()


if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()

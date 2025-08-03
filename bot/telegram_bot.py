import logging

from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

from common.config.config import TELEGRAM_BOT_TOKEN
from common.types.upsert_candidate_input import UpsertCandidateInput
from services.candidates import CandidatesService

COMMAND_USE_GUIDES = {
    "SET_ROLE": "'/setrole [YOUR_ROLE]'\nExample: /setrole backend engineer\n",
    "SET_LOCATION": "'/setlocation [YOUR_LOCATION]'\nExample: /setlocation Argentina\n",
    "SET_STACK": "'/setstack [TECH_1,TECH_2, etc]'\nExample: /setstack python,nodejs\n",
}

class TelegramBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        self.candidates_service = CandidatesService()
        self._register_handlers()

    def _register_handlers(self):
        logging.info('Registering telegram bot handlers')
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(CommandHandler('help', self.help_command))
        self.app.add_handler(CommandHandler('setstack', self.set_tech_stack))
        self.app.add_handler(CommandHandler('setrole', self.set_role))
        self.app.add_handler(CommandHandler('setlocation', self.set_location))
        self.app.add_handler(CommandHandler('myinfo', self.get_my_info))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.non_command_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.info("Received /start command")
        await update.message.reply_text(f"The first thing I need to know about you is your role, let me know it by using the command {COMMAND_USE_GUIDES['SET_ROLE']}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.info("Received /help command")
        await update.message.reply_text("Available commands: \n/start - Configure your job seeking\n/help - Get info")

    async def set_tech_stack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.info("Received /setstack command")
        stack = update.message.text
        if stack is None:
            logging.error("Tech stack was not informed")
            await update.message.reply_text(f"You must inform the stack to continue, command usage: {COMMAND_USE_GUIDES['SET_STACK']}")
            return
        self.candidates_service.upsert(
            id=update.effective_user.id,
            data=UpsertCandidateInput(role=stack)
        )
        await update.message.reply_text(f"Your profile is now complete, I'm gonna use your info to find the best job matches for you")

    async def set_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.info("Received /setrole command")
        role = update.message.text
        if role is None:
            logging.error("Role was not informed")
            await update.message.reply_text(f"You must inform the role to continue, command usage: {COMMAND_USE_GUIDES['SET_ROLE']}")
            return
        self.candidates_service.upsert(
            id=update.effective_user.id,
            data=UpsertCandidateInput(role=role)
        )
        await update.message.reply_text(f"Your role has been set successfully, use {COMMAND_USE_GUIDES['SET_LOCATION']} to continue setting up your profile")


    async def set_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.info("Received /location command")
        location = update.message.text
        if location is None:
            logging.error("Location was not informed")
            await update.message.reply_text(f"You must inform the location to continue, command usage: {COMMAND_USE_GUIDES['SET_LOCATION']}")
            return
        self.candidates_service.upsert(
            id=update.effective_chat.id,
            data=UpsertCandidateInput(role=location)
        )
        await update.message.reply_text("Your location has been set successfully, use /location [YOUR_LOCATION] or /setstack [TECH_1,TECH_2,...] if you haven't yet")

    async def get_my_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass

    async def non_command_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hi! I'm agarralapa bot, your job finder buddy! To start, I need to know what you are looking for, use the command /start to begin")

    def run(self):
        logging.info('Starting telegram bot')
        self.app.run_polling()
        logging.info('Telegram bot started successfully')

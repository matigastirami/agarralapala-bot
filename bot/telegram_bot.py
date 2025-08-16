import logging

from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

from bot.constants import MESSAGES, COMMAND_USE_GUIDES
from common.config.config import TELEGRAM_BOT_TOKEN
from common.types.upsert_candidate_input import UpsertCandidateInput
from services.candidates import CandidatesService
from services.notification_service import NotificationService

class TelegramBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        self.candidates_service = CandidatesService()
        self.notification_service = NotificationService()
        self._register_handlers()

    def _register_handlers(self):
        logging.info('Registering telegram bot handlers')
        self.app.add_handler(CommandHandler('help', self.help_command))
        self.app.add_handler(CommandHandler('setstack', self.set_tech_stack))
        self.app.add_handler(CommandHandler('setrole', self.set_role))
        self.app.add_handler(CommandHandler('setlocation', self.set_location))
        self.app.add_handler(CommandHandler('matches', self.get_matches))
        self.app.add_handler(CommandHandler('myinfo', self.get_my_info))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.non_command_message))

    def _get_message(self, key: str, lang: str = "en", **kwargs) -> str:
        if key not in MESSAGES:
            return "Message not found."
        text = MESSAGES[key].get(lang, MESSAGES[key]["en"])
        return text.format(**kwargs)

    def _detect_language(self, update: Update) -> str:
        lang_code = (update.message.from_user.language_code or "en").lower()
        if lang_code.startswith("es"):
            return "es"
        return "en"

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_lang = self._detect_language(update)
        logging.info(f"Received /help command from {chat_id}")
        await update.message.reply_markdown(self._get_message('help', user_lang))

    async def set_tech_stack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logging.info(f"Received /setstack command from chat_id {chat_id}")
        user_lang = self._detect_language(update)
        args = context.args
        stack = " ".join(args).strip()
        if stack is None or len(stack) == 0:
            logging.error("Tech stack was not informed")
            await update.message.reply_text(f"You must inform the stack to continue, command usage: {COMMAND_USE_GUIDES['SET_STACK']}")
            return
        self.candidates_service.upsert(
            id=chat_id,
            data=UpsertCandidateInput(tech_stack=stack)
        )
        await update.message.reply_markdown(self._get_message('stack_saved', user_lang, stack=stack))

    async def set_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logging.info(f"Received /setrole command from chat_id {chat_id}")
        user_lang = self._detect_language(update)
        args = context.args
        role = " ".join(args).strip()
        print(role)
        if role is None or len(role) == 0:
            logging.error("Role was not informed")
            await update.message.reply_text(f"You must inform the role to continue, command usage: {COMMAND_USE_GUIDES['SET_ROLE']}")
            return
        self.candidates_service.upsert(
            id=chat_id,
            data=UpsertCandidateInput(role=role)
        )
        await update.message.reply_markdown(self._get_message('role_saved', user_lang, role=role))


    async def set_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logging.info(f"Received /location command from chat_id {chat_id}")
        user_lang = self._detect_language(update)
        args = context.args
        location = " ".join(args).strip()
        if location is None or len(location) == 0:
            logging.error("Location was not informed")
            await update.message.reply_text(f"You must inform the location to continue, command usage: {COMMAND_USE_GUIDES['SET_LOCATION']}")
            return
        self.candidates_service.upsert(
            id=chat_id,
            data=UpsertCandidateInput(location=location)
        )
        await update.message.reply_markdown(self._get_message('location_saved', user_lang, location=location))

    async def get_matches(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_lang = self._detect_language(update)
        logging.info(f"Received /matches command from chat_id {chat_id}")
        
        try:
            # Get candidate by telegram chat ID
            candidate = self.candidates_service.get_by_telegram_id(chat_id)
            if not candidate:
                await update.message.reply_markdown(
                    self._get_message('candidate_not_found', user_lang)
                )
                return
            
            # Get matches for this candidate
            from common.database.repositories.matches import MatchesRepository
            matches_repo = MatchesRepository()
            matches = matches_repo.get_matches_by_candidate(candidate.id)
            
            if not matches:
                await update.message.reply_markdown(
                    self._get_message('no_matches_found', user_lang)
                )
                return
            
            # Format and send matches
            message = self.notification_service.format_matches_for_display(matches, user_lang)
            await update.message.reply_markdown(message)
            
        except Exception as e:
            logging.error(f"Error in /matches command: {e}")
            await update.message.reply_markdown(
                self._get_message('error_occurred', user_lang)
            )

    async def get_my_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass

    async def non_command_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logging.info(f"Received non-command message from chat_id {chat_id}")
        user_lang = self._detect_language(update)
        self.candidates_service.upsert(
            id=chat_id,
            data=UpsertCandidateInput(language=user_lang)
        )
        await update.message.reply_markdown(self._get_message('welcome', user_lang))

    def run(self):
        logging.info('Starting telegram bot')
        self.app.run_polling()
        logging.info('Telegram bot started successfully')

    async def send_message(self, chat_id: int, message: str):
        """Send a message to a specific chat ID"""
        try:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=None  # Send as plain text to avoid markdown parsing issues
            )
            logging.info(f"Message sent to chat_id {chat_id}")
        except Exception as e:
            logging.error(f"Error sending message to chat_id {chat_id}: {str(e)}")

    async def send_match_notification(self, chat_id: int, matches: list):
        """Send a formatted match notification"""
        message = self._format_match_notification(matches)
        await self.send_message(chat_id, message)

import logging
import asyncio

from telegram import Update, BotCommand
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

from bot.constants import MESSAGES, COMMAND_USE_GUIDES
from common.config.config import TELEGRAM_BOT_TOKEN
from common.types.upsert_candidate_input import UpsertCandidateInput
from services.candidates import CandidatesService
from services.notification_service import NotificationService

class TelegramBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(self._post_init_setup).build()
        self.candidates_service = CandidatesService()
        self.notification_service = NotificationService()
        self._register_handlers()

    def _setup_commands(self):
        """Set up command suggestions that appear when users type / in Telegram"""
        # Set commands in English (Telegram will show these based on user's language)
        commands = [
            BotCommand("help", "📖 Show help and available commands"),
            BotCommand("setrole", "👨‍💻 Set your job role (e.g., Backend Developer)"),
            BotCommand("setlocation", "📍 Set your location (e.g., Buenos Aires)"),
            BotCommand("setstack", "🛠 Set your tech stack (e.g., Python, Node.js)"),
            BotCommand("matches", "🎯 View your job matches (optional: add search query)"),
            BotCommand("matcheshelp", "🔍 Learn how to filter your matches"),
            BotCommand("myinfo", "👤 View your profile information"),
        ]
        
        # Store commands for later setup when the bot is running
        self._commands_to_setup = commands
        
    async def _set_commands(self, commands):
        """Set the bot commands asynchronously"""
        try:
            await self.app.bot.set_my_commands(commands)
            logging.info("Bot commands set successfully")
        except Exception as e:
            logging.error(f"Failed to set bot commands: {e}")
            
    async def update_commands(self):
        """Update bot commands (can be called to refresh commands)"""
        self._setup_commands()
        
    async def clear_commands(self):
        """Clear all bot commands"""
        try:
            await self.app.bot.delete_my_commands()
            logging.info("Bot commands cleared successfully")
        except Exception as e:
            logging.error(f"Failed to clear bot commands: {e}")
            
    async def get_current_commands(self):
        """Get current bot commands"""
        try:
            commands = await self.app.bot.get_my_commands()
            return commands
        except Exception as e:
            logging.error(f"Failed to get bot commands: {e}")
            return []
            
    def set_commands_sync(self):
        """Set commands synchronously (for testing)"""
        if hasattr(self, '_commands_to_setup'):
            try:
                # Create a new event loop for this operation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._set_commands(self._commands_to_setup))
                loop.close()
                logging.info("Bot commands set successfully (sync)")
            except Exception as e:
                logging.error(f"Failed to set bot commands (sync): {e}")

    def _register_handlers(self):
        logging.info('Registering telegram bot handlers')
        self.app.add_handler(CommandHandler('help', self.help_command))
        self.app.add_handler(CommandHandler('setstack', self.set_tech_stack))
        self.app.add_handler(CommandHandler('setrole', self.set_role))
        self.app.add_handler(CommandHandler('setlocation', self.set_location))
        self.app.add_handler(CommandHandler('matches', self.get_matches))
        self.app.add_handler(CommandHandler('matcheshelp', self.get_matches_help))
        self.app.add_handler(CommandHandler('myinfo', self.get_my_info))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.non_command_message))

    def _escape_markdown(self, text: str) -> str:
        """
        Escape special characters that break Telegram markdown parsing
        """
        if not text:
            return text
        
        # Characters that need escaping in Telegram markdown
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        escaped_text = text
        for char in escape_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        
        return escaped_text

    def _get_message(self, key: str, lang: str = "en", **kwargs) -> str:
        if key not in MESSAGES:
            return "Message not found."
        text = MESSAGES[key].get(lang, MESSAGES[key]["en"])
        
        # Format the message with kwargs
        formatted_text = text.format(**kwargs)
        
        # Escape markdown characters in the formatted text
        return self._escape_markdown(formatted_text)

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
            
            # Get optional query parameter
            query = None
            if context.args:
                query = " ".join(context.args).strip()
                logging.info(f"Filtering matches with query: '{query}' for chat_id {chat_id}")
            
            # Get matches for this candidate with optional filtering
            from common.database.repositories.matches import MatchesRepository
            matches_repo = MatchesRepository()
            
            if query:
                matches = matches_repo.get_matches_by_candidate_with_filter(candidate.id, query)
            else:
                matches = matches_repo.get_matches_by_candidate(candidate.id)
            
            if not matches:
                if query:
                    # Show filtered no results message
                    if user_lang == "es":
                        message = f"🔍 **No se encontraron coincidencias**\nNo hay ofertas que coincidan con '{query}'.\n\n💡 *Tip:* Intenta con términos más generales o usa `/matches` sin filtro para ver todas tus coincidencias."
                    else:
                        message = f"🔍 **No matches found**\nNo job postings match '{query}'.\n\n💡 *Tip:* Try more general terms or use `/matches` without a filter to see all your matches."
                else:
                    message = self._get_message('no_matches_found', user_lang)
                
                await update.message.reply_markdown(message)
                return
            
            # Format and send matches
            message = self.notification_service.format_matches_for_display(matches, user_lang)
            
            # Add filter info if query was used
            if query:
                if user_lang == "es":
                    filter_info = f"\n\n🔍 *Filtrado por:* `{query}`\n💡 *Tip:* Usa `/matches` sin filtro para ver todas tus coincidencias."
                else:
                    filter_info = f"\n\n🔍 *Filtered by:* `{query}`\n💡 *Tip:* Use `/matches` without a filter to see all your matches."
                message += filter_info
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logging.error(f"Error in /matches command: {e}")
            await update.message.reply_markdown(
                self._get_message('error_occurred', user_lang)
            )

    async def get_matches_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_lang = self._detect_language(update)
        logging.info(f"Received /matcheshelp command from chat_id {chat_id}")
        
        try:
            help_message = self._get_message('matches_filter_help', user_lang)
            await update.message.reply_markdown(help_message)
        except Exception as e:
            logging.error(f"Error in /matcheshelp command: {e}")
            await update.message.reply_markdown(
                self._get_message('error_occurred', user_lang)
            )

    async def get_my_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_lang = self._detect_language(update)
        logging.info(f"Received /myinfo command from chat_id {chat_id}")
        
        try:
            # Get candidate by telegram chat ID
            candidate = self.candidates_service.get_by_telegram_id(chat_id)
            if not candidate:
                await update.message.reply_markdown(
                    self._get_message('candidate_not_found', user_lang)
                )
                return
            
            # Format the response
            role = candidate.role or "Not set"
            location = candidate.location or "Not set"
            tech_stack = candidate.tech_stack or "Not set"
            alerts_status = "✅ Active" if candidate.language else "❌ Inactive"
            
            if user_lang == "es":
                message = (
                    f"📝 **Tu información actual**\n\n"
                    f"👨‍💻 **Rol:** `{role}`\n"
                    f"📍 **Ubicación:** `{location}`\n"
                    f"🛠 **Stack tecnológico:** `{tech_stack}`\n"
                    f"🔔 **Alertas de empleo:** {alerts_status}\n\n"
                    f"💡 *Para actualizar tu información usa:*\n"
                    f"• `/setrole <rol>`\n"
                    f"• `/setlocation <ubicación>`\n"
                    f"• `/setstack <stack>`"
                )
            else:
                message = (
                    f"📝 **Your current information**\n\n"
                    f"👨‍💻 **Role:** `{role}`\n"
                    f"📍 **Location:** `{location}`\n"
                    f"🛠 **Tech Stack:** `{tech_stack}`\n"
                    f"🔔 **Job Alerts:** {alerts_status}\n\n"
                    f"💡 *To update your information use:*\n"
                    f"• `/setrole <role>`\n"
                    f"• `/setlocation <location>`\n"
                    f"• `/setstack <stack>`"
                )
            
            await update.message.reply_markdown(message)
            
        except Exception as e:
            logging.error(f"Error in /myinfo command: {e}")
            await update.message.reply_markdown(
                self._get_message('error_occurred', user_lang)
            )

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
        # Set up command suggestions
        self._setup_commands()
        # Start the bot with conflict handling
        try:
            self.app.run_polling(
                allowed_updates=[],
                drop_pending_updates=True,  # Drop any pending updates on startup
                close_loop=False  # Don't close the loop automatically
            )
            logging.info('Telegram bot started successfully')
        except Exception as e:
            if "terminated by other getUpdates request" in str(e):
                logging.error("Telegram bot conflict detected. Another instance may be running.")
                logging.error("This usually happens during deployment. The bot will retry automatically.")
                # Don't exit, let the main loop handle retry
                raise
            else:
                logging.error(f'Error starting telegram bot: {e}')
                raise
        
    async def _post_init_setup(self, application):
        """Set up commands after the bot is initialized"""
        if hasattr(self, '_commands_to_setup'):
            try:
                await self._set_commands(self._commands_to_setup)
                logging.info("Bot commands set successfully after initialization")
            except Exception as e:
                logging.error(f"Failed to set bot commands after initialization: {e}")
        else:
            logging.warning("No commands to set up - _commands_to_setup not found")

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

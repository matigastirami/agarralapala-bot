# Telegram Command Suggestions

This document explains how command suggestions work in the Telegram bot and how to use them.

## Overview

The bot now supports command suggestions that appear when users type `/` in the Telegram chat. This makes it easier for users to discover and use available commands.

## How It Works

### 1. Command Registration

Commands are registered using the Telegram Bot API's `setMyCommands` method. This is done in the `TelegramBot` class:

```python
def _setup_commands(self):
    commands = [
        BotCommand("help", "📖 Show help and available commands"),
        BotCommand("setrole", "👨‍💻 Set your job role (e.g., Backend Developer)"),
        BotCommand("setlocation", "📍 Set your location (e.g., Buenos Aires)"),
        BotCommand("setstack", "🛠 Set your tech stack (e.g., Python, Node.js)"),
        BotCommand("matches", "🎯 View your job matches"),
        BotCommand("myinfo", "👤 View your profile information"),
    ]
```

### 2. Available Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/help` | Show help and available commands | `/help` |
| `/setrole` | Set your job role | `/setrole Backend Developer` |
| `/setlocation` | Set your location | `/setlocation Buenos Aires` |
| `/setstack` | Set your tech stack | `/setstack Python, Node.js` |
| `/matches` | View your job matches | `/matches` |
| `/myinfo` | View your profile information | `/myinfo` |

### 3. User Experience

When a user types `/` in the Telegram chat with the bot:

1. A dropdown menu appears showing all available commands
2. Each command shows its description
3. Users can tap on a command to auto-complete it
4. The command is inserted into the chat input field

## Implementation Details

### Setup Process

1. **Bot Initialization**: Commands are set up when the bot starts
2. **Async Handling**: Commands are set asynchronously to avoid blocking
3. **Error Handling**: Failed command setup is logged but doesn't stop the bot

### Code Structure

```python
class TelegramBot:
    def __init__(self):
        # ... other initialization
        self._register_handlers()
        # Commands are set up in run() method

    def _setup_commands(self):
        # Define commands with descriptions
        # Handle async setup

    async def _set_commands(self, commands):
        # Actually set commands via Telegram API

    def run(self):
        self._setup_commands()  # Set commands before starting
        self.app.run_polling()
```

### Management Methods

The bot provides several methods for managing commands:

- `update_commands()`: Refresh the command list
- `clear_commands()`: Remove all commands
- `get_current_commands()`: Get the current command list

## Testing

You can test the command suggestions using the provided test script:

```bash
python test_telegram_commands.py
```

This script will:
1. Create a bot instance
2. Set up commands
3. Verify commands are set correctly
4. Test command management methods

## Troubleshooting

### Common Issues

1. **Commands not appearing**: Check bot token and permissions
2. **Async errors**: Ensure proper event loop handling
3. **Command limit**: Telegram allows up to 100 commands

### Debug Steps

1. Check logs for command setup errors
2. Verify bot token is valid
3. Test with the provided test script
4. Check Telegram Bot API documentation for updates

## Future Enhancements

Potential improvements:

1. **Language-specific commands**: Show commands in user's language
2. **Dynamic commands**: Show/hide commands based on user state
3. **Command categories**: Group related commands
4. **Usage analytics**: Track which commands are used most

## References

- [Telegram Bot API - setMyCommands](https://core.telegram.org/bots/api#setmycommands)
- [Telegram Bot API - BotCommand](https://core.telegram.org/bots/api#botcommand)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)

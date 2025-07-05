# Telegram Reminder Bot

A simple and efficient Telegram bot that helps you set reminders for important tasks. The bot supports various time formats and persists reminders across bot restarts.

## Features

- ⏰ Set reminders with flexible time formats (seconds, minutes, hours, days)
- 📋 View all pending reminders with remaining time
- 💾 Persistent storage - reminders survive bot restarts
- 🎨 Beautiful Markdown formatting with emojis
- 🔒 Secure token handling via environment variables
- 🛡️ Error handling and input validation
- 📱 Custom keyboard for easy navigation

## Time Formats

- `30s` - 30 seconds
- `5m` - 5 minutes  
- `2h` - 2 hours
- `1d` - 1 day

## Setup

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy your bot token

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variable (Recommended)

For security, set your bot token as an environment variable:

**Windows:**
```cmd
set TELEGRAM_BOT_TOKEN=your_bot_token_here
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN=your_bot_token_here
```

**Or create a `.env` file:**
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot

```bash
python main.py
```

## Usage

### Commands

- `/start` - Welcome message and help
- `/help` - Show help information
- `/remind <time> <message>` - Set a reminder
- `/reminders` - View all pending reminders

### Examples

```
/remind 10m Take out the trash
/remind 2h Call mom
/remind 1d Pay bills
/remind 30s Test reminder
```

## File Structure

```
tg/
├── main.py              # Main bot code
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── reminders.json      # Persistent reminder storage (created automatically)
```

## Features in Detail

### Persistent Storage
Reminders are automatically saved to `reminders.json` and restored when the bot restarts.

### Input Validation
- Time must be at least 1 second
- Time cannot exceed 1 year
- Proper time format validation

### User-Friendly Output
- Time displayed in human-readable format (e.g., "5 minutes" instead of "300 seconds")
- Exact trigger time shown
- Beautiful formatting with emojis and Markdown

### Error Handling
- Graceful error handling for network issues
- Input validation with helpful error messages
- Automatic cleanup of expired reminders

## Security Notes

- The bot token is loaded from environment variables for security
- If no environment variable is set, it falls back to the hardcoded token (not recommended for production)
- User data is stored locally in JSON format

## Troubleshooting

### Bot not responding
1. Check if the bot token is correct
2. Ensure the bot is running without errors
3. Try sending `/start` to the bot

### Reminders not working
1. Check if the bot has permission to send messages
2. Verify the time format is correct
3. Check the console for error messages

### Permission denied errors
Make sure the bot has write permissions in the directory for creating `reminders.json`.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 
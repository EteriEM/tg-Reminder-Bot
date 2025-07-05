# 🤖 Telegram Reminder Bot

A powerful Telegram bot that helps you set reminders with advanced repeat functionality (daily, weekly, monthly). Built with Python and the python-telegram-bot library.

## ✨ Features

### 🔔 Reminder Types
- **One-time reminders** - Set reminders that trigger once
- **Daily reminders** - Repeating reminders every 24 hours
- **Weekly reminders** - Repeating reminders every 7 days
- **Monthly reminders** - Repeating reminders every 30 days

### 🎯 Key Features
- ✅ Easy-to-use command interface
- ✅ Customizable keyboard buttons
- ✅ Persistent storage (reminders survive bot restarts)
- ✅ Flexible time formats (seconds, minutes, hours, days)
- ✅ Separate management for one-time and repeating reminders
- ✅ Automatic cleanup of expired reminders
- ✅ Error handling and user-friendly messages

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd tg
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   .\.venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set your bot token** (optional)
   ```bash
   # Set environment variable
   set TELEGRAM_BOT_TOKEN=your_bot_token_here
   
   # Or edit main.py and replace the default token
   ```

6. **Run the bot**
   ```bash
   # Using the provided scripts
   run_bot.bat          # Windows
   ./run_bot.ps1        # PowerShell
   
   # Or directly
   python main.py
   ```

## 📱 Usage

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and help | `/start` |
| `/help` | Show help information | `/help` |
| `/remind` | Set one-time reminder | `/remind 10m Take out trash` |
| `/daily` | Set daily repeating reminder | `/daily 9h Good morning!` |
| `/weekly` | Set weekly repeating reminder | `/weekly 1d Weekly report` |
| `/monthly` | Set monthly repeating reminder | `/monthly 1d Pay rent` |
| `/reminders` | View one-time reminders | `/reminders` |
| `/repeats` | View repeating reminders | `/repeats` |

### Time Formats

| Format | Description | Examples |
|--------|-------------|----------|
| `s` | Seconds | `30s`, `1s` |
| `m` | Minutes | `5m`, `30m` |
| `h` | Hours | `2h`, `12h` |
| `d` | Days | `1d`, `7d` |

### Examples

**One-time reminders:**
```
/remind 10m Take out the trash
/remind 2h Call mom
/remind 1d Submit report
```

**Repeating reminders:**
```
/daily 9h Good morning!
/weekly 1d Weekly team meeting
/monthly 1d Pay rent
```

## 🏗️ Project Structure

```
tg/
├── main.py              # Main bot application
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Git ignore rules
├── run_bot.bat         # Windows batch script
├── run_bot.ps1         # PowerShell script
├── reminders.json      # Reminder storage (auto-generated)
└── .venv/              # Virtual environment (not in git)
```

## 🔧 Configuration

### Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (optional, has default)

### Bot Token Setup

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the token and set it as an environment variable or replace the default in `main.py`

## 📊 Data Storage

Reminders are stored in `reminders.json` with the following structure:

```json
{
  "user_id": [
    {
      "text": "Reminder message",
      "time": 1234567890.123,
      "id": "unique_reminder_id",
      "repeat": "daily|weekly|monthly|null",
      "original_seconds": 3600
    }
  ]
}
```

## 🛠️ Development

### Running in Development

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Run the bot
python main.py
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
- Check if the bot token is correct
- Ensure the bot is running without errors
- Verify internet connection

**Reminders not triggering:**
- Check if the bot process is still running
- Verify the time format is correct
- Check the console for error messages

**Multiple bot instances:**
- Stop all Python processes: `taskkill /f /im python.exe`
- Restart the bot using the provided scripts

### Logs

The bot outputs logs to the console. Common messages:
- `🤖 Reminder Bot is starting...`
- `Loaded X existing reminders`
- `Error sending reminder: ...`

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the console logs
3. Open an issue on GitHub

---

**Made with ❤️ for better productivity and organization!**
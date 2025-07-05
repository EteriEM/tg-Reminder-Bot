@echo off
echo Starting Telegram Reminder Bot...
echo.
echo Make sure you have set your TELEGRAM_BOT_TOKEN environment variable
echo or the bot will use the default token from the code.
echo.
echo Press Ctrl+C to stop the bot
echo.

REM Kill any existing Python processes (optional)
taskkill /f /im python.exe 2>nul

REM Run the bot
.\.venv\Scripts\python.exe main.py

pause 
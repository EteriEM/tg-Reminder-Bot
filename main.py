import asyncio
import re
import os
import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load bot token from environment variable for security
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7992058301:AAFcFwvoWxzM0q6dHM-faw-yuGCsLMchlng')

# Define the keyboard layout
keyboard = ReplyKeyboardMarkup([
    ['/start', '/remind', '/reminders', '/help']
], resize_keyboard=True)

# Store reminders per user: {user_id: [{'text': ..., 'time': ..., 'id': ...}]}
user_reminders = {}

# File to persist reminders
REMINDERS_FILE = 'reminders.json'

def load_reminders():
    """Load reminders from file"""
    try:
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to integers
                return {int(k): v for k, v in data.items()}
    except Exception as e:
        print(f"Error loading reminders: {e}")
    return {}

def save_reminders():
    """Save reminders to file"""
    try:
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(user_reminders, f, indent=2)
    except Exception as e:
        print(f"Error saving reminders: {e}")

def parse_time(time_str):
    """Parse time string and return seconds"""
    match = re.match(r"(\d+)([smhd])", time_str)
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    return None

def format_time_remaining(seconds):
    """Format remaining time in a user-friendly way"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = (
        "⏰ **Welcome to Reminder Bot!**\n\n"
        "I can help you set reminders for important tasks.\n\n"
        "**Available commands:**\n"
        "• `/remind <time> <message>` - Set a reminder\n"
        "• `/reminders` - View your pending reminders\n"
        "• `/help` - Show this help message\n\n"
        "**Time formats:**\n"
        "• `30s` - 30 seconds\n"
        "• `5m` - 5 minutes\n"
        "• `2h` - 2 hours\n"
        "• `1d` - 1 day\n\n"
        "**Example:** `/remind 10m Take out the trash`"
    )
    await update.message.reply_text(welcome_message, reply_markup=keyboard, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await start(update, context)

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remind command"""
    if len(context.args) < 2:
        await update.message.reply_text(
            '❌ **Usage:** `/remind <time> <message>`\n\n'
            '**Example:** `/remind 10m Take out the trash`',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    time_str = context.args[0]
    reminder_text = ' '.join(context.args[1:])
    seconds = parse_time(time_str)
    
    if seconds is None:
        await update.message.reply_text(
            '❌ **Invalid time format!**\n\n'
            'Use: `s` (seconds), `m` (minutes), `h` (hours), or `d` (days)\n'
            '**Example:** `/remind 10m Take out the trash`',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    if seconds < 1:
        await update.message.reply_text(
            '❌ **Time must be at least 1 second!**',
            reply_markup=keyboard
        )
        return
    
    if seconds > 86400 * 365:  # 1 year
        await update.message.reply_text(
            '❌ **Time cannot exceed 1 year!**',
            reply_markup=keyboard
        )
        return
    
    user_id = update.effective_user.id
    reminder_time = asyncio.get_event_loop().time() + seconds
    reminder_id = f"{user_id}_{reminder_time}_{hash(reminder_text)}"
    
    # Store the reminder
    if user_id not in user_reminders:
        user_reminders[user_id] = []
    
    user_reminders[user_id].append({
        'text': reminder_text, 
        'time': reminder_time,
        'id': reminder_id
    })
    
    save_reminders()
    
    # Calculate when the reminder will trigger
    trigger_time = datetime.now() + timedelta(seconds=seconds)
    time_display = format_time_remaining(seconds)
    
    await update.message.reply_text(
        f'✅ **Reminder set successfully!**\n\n'
        f'📝 **Message:** {reminder_text}\n'
        f'⏰ **Time:** {time_display}\n'
        f'🕐 **Will trigger at:** {trigger_time.strftime("%Y-%m-%d %H:%M:%S")}',
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    async def send_reminder():
        await asyncio.sleep(seconds)
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f'⏰ **Reminder:** {reminder_text}',
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            # Remove the reminder after sending
            if user_id in user_reminders:
                user_reminders[user_id] = [
                    r for r in user_reminders[user_id] 
                    if r['id'] != reminder_id
                ]
                save_reminders()
        except Exception as e:
            print(f"Error sending reminder: {e}")

    asyncio.create_task(send_reminder())

async def reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reminders command"""
    user_id = update.effective_user.id
    reminders_list = user_reminders.get(user_id, [])
    
    if not reminders_list:
        await update.message.reply_text(
            '📭 **You have no pending reminders.**\n\n'
            'Use `/remind <time> <message>` to set one!',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    # Clean up expired reminders
    now = asyncio.get_event_loop().time()
    active_reminders = []
    
    for reminder in reminders_list:
        if reminder['time'] > now:
            active_reminders.append(reminder)
    
    if not active_reminders:
        user_reminders[user_id] = []
        save_reminders()
        await update.message.reply_text(
            '📭 **You have no pending reminders.**\n\n'
            'Use `/remind <time> <message>` to set one!',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    # Update the user's reminders list
    user_reminders[user_id] = active_reminders
    save_reminders()
    
    lines = ['📋 **Your pending reminders:**\n']
    for idx, reminder in enumerate(active_reminders, 1):
        seconds_left = int(reminder['time'] - now)
        time_display = format_time_remaining(seconds_left)
        trigger_time = datetime.fromtimestamp(reminder['time'])
        lines.append(
            f"{idx}. **{reminder['text']}**\n"
            f"   ⏰ {time_display} remaining\n"
            f"   🕐 {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    await update.message.reply_text(
        '\n\n'.join(lines),
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    await update.message.reply_text(
        "🤖 I'm a reminder bot! Use these commands:\n\n"
        "• `/remind <time> <message>` - Set a reminder\n"
        "• `/reminders` - View your pending reminders\n"
        "• `/help` - Show help message",
        reply_markup=keyboard
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=keyboard
        )

if __name__ == '__main__':
    # Load existing reminders
    user_reminders = load_reminders()
    print(f"Loaded {sum(len(reminders) for reminders in user_reminders.values())} existing reminders")
    
    # Create and configure the bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('remind', remind))
    app.add_handler(CommandHandler('reminders', reminders))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    print('🤖 Reminder Bot is starting...')
    print('📝 Use /start to begin')
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        print('\n🛑 Bot stopped by user')
    except Exception as e:
        print(f'❌ Error running bot: {e}')

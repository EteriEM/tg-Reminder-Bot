import asyncio
import re
import os
import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load bot token from environment variable for security
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7992058301:AAFcFwvoWxzM0q6dHM-faw-yuGCsLMchlng')

# Define the keyboard layout with repeat buttons
keyboard = ReplyKeyboardMarkup([
    ['/start', '/remind', '/reminders', '/help'],
    ['/daily', '/weekly', '/monthly', '/repeats']
], resize_keyboard=True)

# Store reminders per user: {user_id: [{'text': ..., 'time': ..., 'id': ..., 'repeat': ...}]}
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

def get_next_repeat_time(current_time, repeat_type):
    """Calculate the next repeat time based on repeat type"""
    if repeat_type == 'daily':
        return current_time + 86400  # 24 hours
    elif repeat_type == 'weekly':
        return current_time + 86400 * 7  # 7 days
    elif repeat_type == 'monthly':
        # Approximate 30 days for monthly
        return current_time + 86400 * 30
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = (
        "⏰ **Welcome to Reminder Bot!**\n\n"
        "I can help you set reminders for important tasks.\n\n"
        "**Available commands:**\n"
        "• `/remind <time> <message>` - Set a one-time reminder\n"
        "• `/daily <time> <message>` - Set a daily repeating reminder\n"
        "• `/weekly <time> <message>` - Set a weekly repeating reminder\n"
        "• `/monthly <time> <message>` - Set a monthly repeating reminder\n"
        "• `/reminders` - View your pending reminders\n"
        "• `/repeats` - View your repeating reminders\n"
        "• `/help` - Show this help message\n\n"
        "**Time formats:**\n"
        "• `30s` - 30 seconds\n"
        "• `5m` - 5 minutes\n"
        "• `2h` - 2 hours\n"
        "• `1d` - 1 day\n\n"
        "**Examples:**\n"
        "• `/remind 10m Take out the trash`\n"
        "• `/daily 9h Good morning!`\n"
        "• `/weekly 1d Weekly report`"
    )
    await update.message.reply_text(welcome_message, reply_markup=keyboard, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await start(update, context)

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remind command for one-time reminders"""
    await create_reminder(update, context, repeat_type=None)

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command for daily repeating reminders"""
    await create_reminder(update, context, repeat_type='daily')

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /weekly command for weekly repeating reminders"""
    await create_reminder(update, context, repeat_type='weekly')

async def monthly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /monthly command for monthly repeating reminders"""
    await create_reminder(update, context, repeat_type='monthly')

async def create_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, repeat_type=None):
    """Create a reminder with optional repeat functionality"""
    if len(context.args) < 2:
        repeat_text = f" for {repeat_type} reminder" if repeat_type else ""
        await update.message.reply_text(
            f'❌ **Usage:** `/{context.args[0] if context.args else "remind"} <time> <message>`{repeat_text}\n\n'
            f'**Example:** `/{context.args[0] if context.args else "remind"} 10m Take out the trash`',
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
            f'**Example:** `/{context.args[0] if context.args else "remind"} 10m Take out the trash`',
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
    reminder_id = f"{user_id}_{reminder_time}_{hash(reminder_text)}_{repeat_type or 'once'}"
    
    # Store the reminder
    if user_id not in user_reminders:
        user_reminders[user_id] = []
    
    user_reminders[user_id].append({
        'text': reminder_text, 
        'time': reminder_time,
        'id': reminder_id,
        'repeat': repeat_type,
        'original_seconds': seconds
    })
    
    save_reminders()
    
    # Calculate when the reminder will trigger
    trigger_time = datetime.now() + timedelta(seconds=seconds)
    time_display = format_time_remaining(seconds)
    
    repeat_info = f"\n🔄 **Repeat:** {repeat_type.title()}" if repeat_type else ""
    
    await update.message.reply_text(
        f'✅ **Reminder set successfully!**\n\n'
        f'📝 **Message:** {reminder_text}\n'
        f'⏰ **Time:** {time_display}\n'
        f'🕐 **Will trigger at:** {trigger_time.strftime("%Y-%m-%d %H:%M:%S")}{repeat_info}',
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    async def send_reminder():
        while True:
            await asyncio.sleep(seconds)
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=f'⏰ **Reminder:** {reminder_text}',
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
                # If it's a repeating reminder, schedule the next one
                if repeat_type:
                    next_time = get_next_repeat_time(asyncio.get_event_loop().time(), repeat_type)
                    if next_time:
                        # Update the reminder time for the next occurrence
                        for reminder in user_reminders.get(user_id, []):
                            if reminder['id'] == reminder_id:
                                reminder['time'] = next_time
                                save_reminders()
                                break
                        # Continue the loop for the next reminder
                        seconds = reminder['original_seconds']
                        continue
                
                # Remove the reminder after sending (for non-repeating reminders)
                if user_id in user_reminders:
                    user_reminders[user_id] = [
                        r for r in user_reminders[user_id] 
                        if r['id'] != reminder_id
                    ]
                    save_reminders()
                break
                
            except Exception as e:
                print(f"Error sending reminder: {e}")
                break

    asyncio.create_task(send_reminder())

async def reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reminders command - show one-time reminders"""
    user_id = update.effective_user.id
    reminders_list = user_reminders.get(user_id, [])
    
    # Filter for one-time reminders only
    one_time_reminders = [r for r in reminders_list if not r.get('repeat')]
    
    if not one_time_reminders:
        await update.message.reply_text(
            '📭 **You have no pending one-time reminders.**\n\n'
            'Use `/remind <time> <message>` to set one!',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    # Clean up expired reminders
    now = asyncio.get_event_loop().time()
    active_reminders = []
    
    for reminder in one_time_reminders:
        if reminder['time'] > now:
            active_reminders.append(reminder)
    
    if not active_reminders:
        # Remove expired one-time reminders
        user_reminders[user_id] = [r for r in user_reminders[user_id] if r.get('repeat')]
        save_reminders()
        await update.message.reply_text(
            '📭 **You have no pending one-time reminders.**\n\n'
            'Use `/remind <time> <message>` to set one!',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    # Update the user's reminders list
    user_reminders[user_id] = [r for r in user_reminders[user_id] if r.get('repeat') or r in active_reminders]
    save_reminders()
    
    lines = ['📋 **Your pending one-time reminders:**\n']
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

async def repeats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /repeats command - show repeating reminders"""
    user_id = update.effective_user.id
    reminders_list = user_reminders.get(user_id, [])
    
    # Filter for repeating reminders only
    repeating_reminders = [r for r in reminders_list if r.get('repeat')]
    
    if not repeating_reminders:
        await update.message.reply_text(
            '🔄 **You have no repeating reminders.**\n\n'
            'Use `/daily`, `/weekly`, or `/monthly` to set repeating reminders!',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    lines = ['🔄 **Your repeating reminders:**\n']
    for idx, reminder in enumerate(repeating_reminders, 1):
        trigger_time = datetime.fromtimestamp(reminder['time'])
        repeat_type = reminder['repeat'].title()
        lines.append(
            f"{idx}. **{reminder['text']}**\n"
            f"   🔄 {repeat_type}\n"
            f"   🕐 Next: {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}"
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
        "• `/remind <time> <message>` - Set a one-time reminder\n"
        "• `/daily <time> <message>` - Set a daily repeating reminder\n"
        "• `/weekly <time> <message>` - Set a weekly repeating reminder\n"
        "• `/monthly <time> <message>` - Set a monthly repeating reminder\n"
        "• `/reminders` - View your one-time reminders\n"
        "• `/repeats` - View your repeating reminders\n"
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
    app.add_handler(CommandHandler('daily', daily))
    app.add_handler(CommandHandler('weekly', weekly))
    app.add_handler(CommandHandler('monthly', monthly))
    app.add_handler(CommandHandler('reminders', reminders))
    app.add_handler(CommandHandler('repeats', repeats))
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

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os
import asyncio
from flask import Flask
import threading

TOKEN = "8417018128:AAHAm_2-OP22yzWv3VFPvOGT6-HTNgmspT4"

# Create Flask app for Render health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! 🤖 I'm a Calculator Bot.\n"
        "Send me a math expression like:\n"
        "`2 + 3 * 4`\n"
        "and I'll calculate it!",
        parse_mode="Markdown"
    )

def safe_eval(expr):
    allowed_chars = "0123456789+-*/(). "
    if all(char in allowed_chars for char in expr):
        try:
            return eval(expr, {"__builtins__": None}, {})
        except Exception:
            return "❌ Invalid expression"
    else:
        return "❌ Only numbers and + - * / ( ) are allowed!"

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    result = safe_eval(user_input)
    await update.message.reply_text(f"✅ Result: `{result}`", parse_mode="Markdown")

def run_bot():
    """Run the Telegram bot"""
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))
    
    print("🤖 Bot is running...")
    
    # Run the bot with the event loop
    loop.run_until_complete(bot_app.initialize())
    loop.run_until_complete(bot_app.start())
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(bot_app.stop())
        loop.run_until_complete(bot_app.shutdown())

def run_flask():
    """Run Flask server for Render"""
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run the bot
    run_bot()

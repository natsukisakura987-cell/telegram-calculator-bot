from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
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
    # Use Application instead of ApplicationBuilder
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))
    
    print("🤖 Bot is running...")
    
    # Run the bot with polling
    application.run_polling()

def run_flask():
    """Run Flask server for Render"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run the bot
    run_bot()
    

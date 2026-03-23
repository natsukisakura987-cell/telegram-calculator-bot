from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

TOKEN = "8417018128:AAHAm_2-OP22yzWv3VFPvOGT6-HTNgmspT4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! 🤖 I'm a Calculator Bot.\n"
        "Send me a math expression like:\n"
        "2 + 3 * 4\n"
        "and I'll calculate it!"
    )

def safe_eval(expr):
    allowed_chars = "0123456789+-*/(). "
    if all(c in allowed_chars for c in expr):
        try:
            return eval(expr, {"__builtins__": None}, {})
        except Exception:
            return "❌ Invalid expression"
    else:
        return "❌ Only numbers and + - * / ( ) are allowed!"

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    result = safe_eval(user_input)
    await update.message.reply_text(f"✅ Result: {result}")

if __name__ == "__main__":
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))
    
    print("🤖 Bot is starting...")
    
    # Run the bot - this handles the event loop internally
    app.run_polling(allowed_updates=None)

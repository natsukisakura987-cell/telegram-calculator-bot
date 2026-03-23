from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
TOKEN = "8417018128:AAHAm_2-OP22yzWv3VFPvOGT6-HTNgmspT4"

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
    await update.message.reply_text(f"✅Result: `{result}`", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    # Text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

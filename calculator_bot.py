from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import math
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8417018128:AAHk55Bmr2Nx6sgK2lQ5ddfz8zsOE5fduYw"

# HTTP server for Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_http_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Simple Calculator*\n\n"
        "Send me any calculation:\n"
        "• `5 + 3` = 8\n"
        "• `10 * 2` = 20\n"
        "• `20 / 4` = 5\n"
        "• `2^3` = 8\n"
        "• `√16` = 4\n"
        "• `sin(30)` = 0.5\n\n"
        "Just type and I'll calculate!",
        parse_mode="Markdown"
    )

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        
        # Basic calculator - no equations
        # Replace symbols
        calc_text = text.replace('√', 'sqrt')
        calc_text = calc_text.replace('^', '**')
        
        # Handle sin, cos, tan
        import re
        def trig(m):
            func = m.group(1)
            deg = float(m.group(2))
            rad = math.radians(deg)
            return str(getattr(math, func)(rad))
        
        calc_text = re.sub(r'(sin|cos|tan)\((\d+)\)', trig, calc_text)
        
        # Handle sqrt
        import re
        def sq(m):
            return str(math.sqrt(float(m.group(1))))
        
        calc_text = re.sub(r'sqrt\((\d+)\)', sq, calc_text)
        
        # Calculate
        result = eval(calc_text)
        
        # Format result
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 4)
        
        await update.message.reply_text(f"✅ {text} = {result}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {text}\n\nTry: 5+3, 10*2, √16, sin(30)")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is active!")

def main():
    # Start HTTP server
    threading.Thread(target=run_http_server, daemon=True).start()
    
    print("🤖 Calculator Bot is starting...")
    
    # Start bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))
    
    app.run_polling()

if __name__ == "__main__":
    main()

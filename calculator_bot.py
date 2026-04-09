from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import math
import os
import threading
import re
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

def calculate(text):
    try:
        original = text
        
        # Fix: Replace √ with sqrt properly
        text = text.replace('√', 'math.sqrt')
        
        # Handle sqrt with parentheses or without
        # √144 -> math.sqrt(144)
        text = re.sub(r'math\.sqrt(\d+)', r'math.sqrt(\1)', text)
        
        # Replace ^ with **
        text = text.replace('^', '**')
        
        # Handle sin, cos, tan
        def trig(m):
            func = m.group(1)
            deg = float(m.group(2))
            rad = math.radians(deg)
            if func == 'sin':
                return str(math.sin(rad))
            elif func == 'cos':
                return str(math.cos(rad))
            elif func == 'tan':
                return str(math.tan(rad))
            return m.group(0)
        
        text = re.sub(r'(sin|cos|tan)\((\d+)\)', trig, text)
        
        # Safe evaluation
        allowed_names = {
            'math': math,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'pi': math.pi
        }
        
        result = eval(text, {"__builtins__": {}}, allowed_names)
        
        # Format result
        if isinstance(result, float):
            if abs(result - round(result)) < 0.0001:
                result = int(round(result))
            else:
                result = round(result, 6)
        
        return f"✅ {original} = {result}"
        
    except Exception as e:
        return f"❌ Error: {original}\n\nTry: 5+3, 10*2, √16, sin(30)"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Simple Calculator*\n\n"
        "Send me any calculation:\n"
        "• `5 + 3` = 8\n"
        "• `10 * 2` = 20\n"
        "• `√16` = 4\n"
        "• `2^3` = 8\n"
        "• `sin(30)` = 0.5\n\n"
        "Just type and I'll calculate!",
        parse_mode="Markdown"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is active!")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = calculate(update.message.text)
    await update.message.reply_text(result)

def main():
    # Start HTTP server
    threading.Thread(target=run_http_server, daemon=True).start()
    
    print("🤖 Calculator Bot is starting...")
    
    # Start bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()

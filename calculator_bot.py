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

def calculate(expression):
    try:
        original = expression
        
        # Clean the expression
        calc = expression.strip()
        
        # Replace symbols
        calc = calc.replace('×', '*')
        calc = calc.replace('÷', '/')
        calc = calc.replace('^', '**')
        calc = calc.replace('√', 'math.sqrt')
        
        # Handle sqrt without parentheses: math.sqrt144 -> math.sqrt(144)
        import re
        calc = re.sub(r'math\.sqrt(\d+)', r'math.sqrt(\1)', calc)
        
        # Handle sin, cos, tan
        calc = calc.replace('sin', 'math.sin')
        calc = calc.replace('cos', 'math.cos')
        calc = calc.replace('tan', 'math.tan')
        
        # Convert degrees to radians for trig functions
        def deg_to_rad(match):
            func = match.group(1)
            angle = match.group(2)
            return f'{func}(math.radians({angle}))'
        
        calc = re.sub(r'(math\.(?:sin|cos|tan))\((\d+)\)', deg_to_rad, calc)
        
        # Simple evaluation
        result = eval(calc, {'math': math})
        
        # Format result
        if isinstance(result, float):
            if abs(result - round(result)) < 0.0001:
                result = int(round(result))
            else:
                result = round(result, 6)
        
        return f"✅ {original} = {result}"
        
    except Exception as e:
        return f"❌ Error: {original}\n\nUse: 5+3, 25*4, sqrt(144), sin(30)"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Calculator Bot*\n\n"
        "Send me any calculation:\n"
        "• `5 + 3` = 8\n"
        "• `25 * 4` = 100\n"
        "• `sqrt(144)` = 12\n"
        "• `sin(30)` = 0.5\n"
        "• `2^3` = 8\n\n"
        "Bot by @KanKann_calc_bot",
        parse_mode="Markdown"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot is active!")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = calculate(update.message.text)
    await update.message.reply_text(result)

def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    
    print("🤖 Calculator Bot is starting...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()

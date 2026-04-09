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

def calculate(expression):
    try:
        original = expression
        
        # Replace × with *
        expression = expression.replace('×', '*')
        expression = expression.replace('÷', '/')
        
        # Replace ^ with **
        expression = expression.replace('^', '**')
        
        # Handle sqrt - convert sqrt16 to sqrt(16)
        expression = re.sub(r'sqrt(\d+)', r'sqrt(\1)', expression)
        
        # Handle sin, cos, tan
        expression = expression.replace('sin', 'math.sin')
        expression = expression.replace('cos', 'math.cos')
        expression = expression.replace('tan', 'math.tan')
        
        # Convert degrees to radians for trig
        def convert_trig(m):
            func = m.group(1)
            angle = m.group(2)
            return f'{func}(math.radians({angle}))'
        
        expression = re.sub(r'(math\.(?:sin|cos|tan))\((\d+)\)', convert_trig, expression)
        
        # Evaluate safely
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        
        # Format result
        if isinstance(result, float):
            if abs(result - round(result)) < 0.0001:
                result = int(round(result))
            else:
                result = round(result, 6)
        
        return f"✅ {original} = {result}"
        
    except Exception as e:
        return f"❌ Error: {original}\n\nPlease use:\n• 25*4 or 25×4\n• sqrt(144)\n• 5+3\n• sin(30)"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Calculator Bot*\n\n"
        "Send me any calculation:\n\n"
        "• `25 * 4` or `25×4` = 100\n"
        "• `sqrt(144)` = 12\n"
        "• `5 + 3` = 8\n"
        "• `10 / 2` = 5\n"
        "• `2^3` = 8\n"
        "• `sin(30)` = 0.5\n\n"
        "*Note:* Use `sqrt()` for square roots\n\n"
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

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
        
        # Replace √ with sqrt()
        expression = expression.replace('√', 'sqrt(')
        
        # Add closing parenthesis if missing: sqrt(16 -> sqrt(16)
        import re
        expression = re.sub(r'sqrt\((\d+)(?!\))', r'sqrt(\1)', expression)
        
        # Replace ^ with **
        expression = expression.replace('^', '**')
        
        # Handle sin, cos, tan
        expression = expression.replace('sin', 'math.sin')
        expression = expression.replace('cos', 'math.cos')
        expression = expression.replace('tan', 'math.tan')
        
        # Convert degrees to radians for trig
        # sin(30) -> math.sin(math.radians(30))
        def convert_trig(m):
            func = m.group(1)
            angle = m.group(2)
            return f'{func}(math.radians({angle}))'
        
        expression = re.sub(r'(math\.(?:sin|cos|tan))\((\d+)\)', convert_trig, expression)
        
        # Evaluate
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        
        # Format result
        if isinstance(result, float):
            if abs(result - round(result)) < 0.0001:
                result = int(round(result))
            else:
                result = round(result, 6)
        
        return f"✅ {original} = {result}"
        
    except Exception as e:
        return f"❌ Error: {original}\n\nTry: 5+3, 10*2, sqrt(16), sin(30)"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Simple Calculator*\n\n"
        "Send me any calculation:\n"
        "• `5 + 3` = 8\n"
        "• `10 * 2` = 20\n"
        "• `sqrt(16)` = 4\n"
        "• `2^3` = 8\n"
        "• `sin(30)` = 0.5\n\n"
        "*Note:* Use `sqrt(16)` instead of √16\n\n"
        "Bot by @KanKann_calc_bot",
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

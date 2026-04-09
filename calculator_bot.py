from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import math
import re
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8417018128:AAHk55Bmr2Nx6sgK2lQ5ddfz8zsOE5fduYw"

# HTTP server for Render (keeps bot alive)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_http_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# Simple math solver
def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Basic arithmetic only (no equations)
        # Remove any letters (equations won't work)
        if '=' in expr or 'x' in expr.lower():
            return "I can only solve basic math problems like:\n• 5+3\n• 10*2\n• √16+2\n• sin(30)+cos(60)"
        
        # Handle √
        expr = expr.replace('√', 'sqrt')
        expr = expr.replace('^', '**')
        
        # Handle trig functions
        def trig_calc(m):
            func = m.group(1)
            deg = float(m.group(2))
            rad = math.radians(deg)
            if func == 'sin':
                return str(round(math.sin(rad), 6))
            if func == 'cos':
                return str(round(math.cos(rad), 6))
            if func == 'tan':
                return str(round(math.tan(rad), 6))
            return m.group(0)
        
        expr = re.sub(r'(sin|cos|tan)\((\d+)\)', trig_calc, expr)
        
        # Handle sqrt
        def sqrt_calc(m):
            return str(math.sqrt(float(m.group(1))))
        
        expr = re.sub(r'sqrt\((\d+)\)', sqrt_calc, expr)
        
        # Evaluate
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 6)
        
        return f"✅ {original}\n= {result}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nTry simple math like:\n• 5+3\n• √16+2\n• sin(30)+cos(60)"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Math Bot*\n\n"
        "I can solve:\n"
        "• Basic math: `5+3`, `10*2`\n"
        "• Square roots: `√16+2`\n"
        "• Trigonometry: `sin(30)+cos(60)`\n"
        "• Powers: `2^3+4`\n\n"
        "Bot by @KanKann_calc_bot",
        parse_mode="Markdown"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is working!")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result, parse_mode="Markdown")

def main():
    # Start HTTP server for Render
    thread = threading.Thread(target=run_http_server, daemon=True)
    thread.start()
    
    print("🤖 Bot is starting...")
    
    # Start bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()

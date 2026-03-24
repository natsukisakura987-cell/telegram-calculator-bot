from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sympy as sp
import math
import re
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8417018128:AAHAm_2-OP22yzWv3VFPvOGT6-HTNgmspT4"

# ----- HTTP server for Render -----
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_http_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# ----- Math solver (handles sin(30)+cos(60) etc.) -----
def solve_math(expr):
    try:
        expr = expr.strip()

        # 1. Equations like 3x+2=5
        if '=' in expr:
            left, right = expr.split('=', 1)
            x = sp.Symbol('x')
            eq = sp.Eq(sp.sympify(left), sp.sympify(right))
            solutions = sp.solve(eq, x)
            return f"✅ *Solution:* `{expr}`\n\nx = `{solutions}`"

        # 2. Replace sin(30), cos(60), etc. with numeric values
        def trig_repl(m):
            func = m.group(1)
            deg = float(m.group(2))
            rad = math.radians(deg)
            if func == 'sin':
                return str(math.sin(rad))
            if func == 'cos':
                return str(math.cos(rad))
            return str(math.tan(rad))

        processed = re.sub(r'(sin|cos|tan)\((\d+(?:\.\d+)?)\)', trig_repl, expr)

        # 3. Evaluate the whole expression numerically
        result = eval(processed)
        return f"✅ *Result:* `{expr}`\n= `{result}`"

    except Exception as e:
        return f"❌ *Error:* {e}\n\nTry:\n`3x+2=5`\n`sin(30)+cos(60)`"

# ----- Telegram handlers -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Universal Math Bot* 🧮\n\n"
        "Type any math problem:\n"
        "• `3x + 2 = 5`\n"
        "• `sin(30) + cos(60)`\n"
        "• `5 + 3 * 2`",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result, parse_mode="Markdown")

# ----- Main -----
def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    print("🤖 Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

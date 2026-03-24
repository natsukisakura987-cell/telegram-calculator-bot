from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sympy as sp
import math
import re
import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8417018128:AAHAm_2-OP22yzWv3VFPvOGT6-HTNgmspT4"

# ---------- Simple HTTP handler for Render's port check ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_http_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# ---------- Telegram bot handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Advanced Math Bot* 🧮\n\n"
        "I can solve various math problems!\n\n"
        "*📐 Trigonometry:*\n`sin(30)`, `cos(45)`, `tan(60)`\n\n"
        "*📊 Calculus:*\n`differentiate x^2`\n`integrate 2x`\n\n"
        "*🔢 Algebra:*\n`solve x^2 - 4 = 0`\n`simplify (x+1)^2`\n\n"
        "*➕ Basic Math:*\n`5 + 3`, `10 * 2`, `(4+6)/2`\n\n"
        "Just type your math problem!",
        parse_mode="Markdown"
    )

def solve_math_problem(query):
    try:
        query = query.lower().strip()

        # Differentiate
        if any(kw in query for kw in ('differentiate', 'derivative', 'diff')):
            expr_str = re.sub(r'(differentiate|derivative|diff)', '', query).strip()
            x = sp.Symbol('x')
            expr = sp.sympify(expr_str)
            result = sp.diff(expr, x)
            return f"📈 *Derivative:*\n`d/dx ({expr_str})`\n= `{result}`"

        # Integrate
        elif any(kw in query for kw in ('integrate', 'integral', 'int')):
            expr_str = re.sub(r'(integrate|integral|int)', '', query).strip()
            x = sp.Symbol('x')
            expr = sp.sympify(expr_str)
            result = sp.integrate(expr, x)
            return f"📊 *Integral:*\n`∫ {expr_str} dx`\n= `{result} + C`"

        # Solve equations
        elif 'solve' in query:
            equation = re.sub(r'solve', '', query).strip()
            x = sp.Symbol('x')
            result = sp.solve(equation, x)
            return f"🔢 *Solution:*\n`{equation}`\n= `{result}`"

        # Simplify
        elif 'simplify' in query:
            expr_str = re.sub(r'simplify', '', query).strip()
            expr = sp.sympify(expr_str)
            result = sp.simplify(expr)
            return f"🔄 *Simplified:*\n`{expr_str}`\n= `{result}`"

        # Factor
        elif 'factor' in query:
            expr_str = re.sub(r'factor', '', query).strip()
            expr = sp.sympify(expr_str)
            result = sp.factor(expr)
            return f"🔍 *Factored:*\n`{expr_str}`\n= `{result}`"

        # Expand
        elif 'expand' in query:
            expr_str = re.sub(r'expand', '', query).strip()
            expr = sp.sympify(expr_str)
            result = sp.expand(expr)
            return f"📤 *Expanded:*\n`{expr_str}`\n= `{result}`"

        # Trigonometry (degrees)
        trig_match = re.search(r'(sin|cos|tan)\((\d+)\)', query)
        if trig_match:
            func = trig_match.group(1)
            angle = float(trig_match.group(2))
            rad = math.radians(angle)
            if func == 'sin':
                result = math.sin(rad)
            elif func == 'cos':
                result = math.cos(rad)
            else:
                result = math.tan(rad)
            return f"📐 *{func}({angle}°)*\n= `{result:.6f}`"

        # Basic arithmetic
        allowed = "0123456789+-*/(). "
        if all(c in allowed or c.isspace() for c in query):
            result = eval(query)
            return f"✅ *Result:*\n`{query}`\n= `{result}`"
        else:
            return ("❌ *I couldn't understand your query*\n\n"
                    "*Try these commands:*\n"
                    "`differentiate x^2`\n`integrate 2x`\n`solve x^2 - 4 = 0`\n"
                    "`sin(30)`\n`5 + 3`")

    except Exception as e:
        return f"❌ *Error:* {str(e)}"

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math_problem(update.message.text)
    await update.message.reply_text(result, parse_mode="Markdown")

# ---------- Main ----------
def main():
    # Start HTTP server in a background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Start Telegram bot
    print("🤖 Advanced Math Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

    # Keep the main thread alive with the bot
    app.run_polling()

if __name__ == "__main__":
    main()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sympy as sp
import math
import re
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8417018128:AAHAm_2-OP22yzWv3VFPvOGT6-HTNgmspT4"

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

# Math solver
def solve_math(expr):
    try:
        expr = expr.strip()
        
        # Convert √ to sqrt
        expr = expr.replace('√', 'sqrt')
        
        # Convert ^ to **
        expr = expr.replace('^', '**')
        
        # Fix: Add * between number and variable (2x -> 2*x)
        expr = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr)
        
        # 1. Equations like 3x+2=5 or 2x+cos(60)=5
        if '=' in expr:
            left, right = expr.split('=', 1)
            try:
                # Convert trig functions in equation
                def trig_repl_eq(m):
                    func = m.group(1)
                    deg = float(m.group(2))
                    rad = math.radians(deg)
                    if func == 'sin':
                        return str(math.sin(rad))
                    if func == 'cos':
                        return str(math.cos(rad))
                    if func == 'tan':
                        return str(math.tan(rad))
                    return m.group(0)
                
                left_processed = re.sub(r'(sin|cos|tan)\((\d+(?:\.\d+)?)\)', trig_repl_eq, left)
                right_processed = re.sub(r'(sin|cos|tan)\((\d+(?:\.\d+)?)\)', trig_repl_eq, right)
                
                x = sp.Symbol('x')
                eq = sp.Eq(sp.sympify(left_processed), sp.sympify(right_processed))
                solutions = sp.solve(eq, x)
                return f"✅ *Solution:* `{expr}`\n\nx = `{solutions}`"
            except:
                # Fallback to regular solving
                x = sp.Symbol('x')
                eq = sp.Eq(sp.sympify(left), sp.sympify(right))
                solutions = sp.solve(eq, x)
                return f"✅ *Solution:* `{expr}`\n\nx = `{solutions}`"
        
        # 2. Replace trig functions with numeric values
        def trig_repl(m):
            func = m.group(1)
            deg = float(m.group(2))
            rad = math.radians(deg)
            if func == 'sin':
                return str(math.sin(rad))
            if func == 'cos':
                return str(math.cos(rad))
            if func == 'tan':
                return str(math.tan(rad))
            return m.group(0)
        
        processed = re.sub(r'(sin|cos|tan)\((\d+(?:\.\d+)?)\)', trig_repl, expr)
        
        # Handle sqrt
        def sqrt_repl(m):
            num = float(m.group(1))
            return str(math.sqrt(num))
        
        processed = re.sub(r'sqrt\((\d+(?:\.\d+)?)\)', sqrt_repl, processed)
        
        # 3. Evaluate the whole expression numerically
        result = eval(processed)
        
        # Format result - remove .0 if it's a whole number
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        
        return f"✅ *Result:* `{expr}`\n= `{result}`"
        
    except Exception as e:
        return f"❌ *Error:* {str(e)}\n\n*Try:*\n`3x+2=5`\n`2x+cos(60)=5`\n`√16+2`"

# Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Universal Math Bot* 🧮\n\n"
        "Type any math problem!\n\n"
        "*Examples:*\n"
        "• `3x+2=5` → x = 1\n"
        "• `2x+cos(60)=5` → x = 2.25\n"
        "• `√16+2` → 6\n"
        "• `sin(30)+cos(60)` → 1.0\n"
        "• `2^3+4` → 12\n\n"
        "Just type and get answer!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result, parse_mode="Markdown")

# Main
def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    print("🤖 Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

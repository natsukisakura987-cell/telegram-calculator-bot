from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sympy as sp
import math
import re
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8417018128:AAHAm_2-OP22yzWv3VFPvOGT6-HTNgmspT4"

# ---------- HTTP server for Render ----------
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

# ---------- Math Solver (Universal) ----------
def solve_math(expr):
    try:
        expr = expr.strip()
        
        # 1. Equation solving: 3x+2=5
        if '=' in expr:
            left, right = expr.split('=', 1)
            left_expr = sp.sympify(left)
            right_expr = sp.sympify(right)
            equation = sp.Eq(left_expr, right_expr)
            x = sp.Symbol('x')
            solutions = sp.solve(equation, x)
            return f"🔢 *Solution:*\n`{expr}`\n\nx = `{solutions}`"
        
        # 2. Calculus: d/dx
        if expr.startswith('d/') or 'derivative' in expr.lower():
            match = re.search(r'[dD]/[dD][xX]\s*(.+)', expr)
            if match:
                func = match.group(1).strip()
            else:
                func = re.sub(r'(derivative|of)', '', expr, flags=re.IGNORECASE).strip()
            x = sp.Symbol('x')
            f = sp.sympify(func)
            result = sp.diff(f, x)
            return f"📈 *Derivative:*\n`d/dx ({func})`\n= `{result}`"
        
        # 3. Integration
        if 'integral' in expr.lower() or 'integrate' in expr.lower() or '∫' in expr:
            match = re.search(r'[∫]?\s*([^dx]+)\s*dx', expr)
            if match:
                func = match.group(1).strip()
            else:
                func = re.sub(r'(integrate|integral|∫)', '', expr, flags=re.IGNORECASE).strip()
            x = sp.Symbol('x')
            f = sp.sympify(func)
            result = sp.integrate(f, x)
            return f"📊 *Integral:*\n`∫ {func} dx`\n= `{result} + C`"
        
        # 4. Handle expressions with trig functions and operations
        # Replace trig functions with sympy format
        processed = expr.lower()
        
        # Convert sin(30) to sin(30*pi/180) for degrees
        def convert_trig(match):
            func = match.group(1)
            angle = match.group(2)
            return f"{func}({angle}*pi/180)"
        
        # Apply conversion to all trig functions
        processed = re.sub(r'(sin|cos|tan)\((\d+)\)', convert_trig, processed)
        
        # Try to evaluate as a complete expression
        try:
            # Create symbols
            x = sp.Symbol('x')
            # Parse the expression
            f = sp.sympify(processed)
            # Evaluate numerically if possible
            result_numeric = float(sp.N(f))
            return f"✅ *Result:*\n`{expr}`\n= `{result_numeric}`"
        except:
            # If can't evaluate numerically, try simplifying
            try:
                x = sp.Symbol('x')
                f = sp.sympify(processed)
                simplified = sp.simplify(f)
                return f"🧮 *Expression:* `{expr}`\n\n🔄 *Simplified:* `{simplified}`"
            except:
                pass
        
        # 5. Fallback - general expression
        try:
            f = sp.sympify(expr)
            simplified = sp.simplify(f)
            result_numeric = float(sp.N(f))
            return f"✅ *Result:*\n`{expr}`\n= `{result_numeric}`"
        except:
            try:
                f = sp.sympify(expr)
                simplified = sp.simplify(f)
                return f"🧮 *Expression:* `{expr}`\n\n🔄 *Simplified:* `{simplified}`"
            except Exception as e:
                return f"❌ *Error:* {str(e)}\n\n*Try:*\n`3x + 2 = 5`\n`sin(30) + cos(60)`\n`d/dx x^2`"
        
    except Exception as e:
        return f"❌ *Error:* {str(e)}\n\n*Try:*\n`3x + 2 = 5`\n`sin(30) + cos(60)`\n`d/dx x^2`"

# ---------- Telegram Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Universal Math Bot* 🧮\n\n"
        "Just type any math expression!\n\n"
        "*Examples:*\n"
        "`3x + 2 = 5` → solve equation\n"
        "`sin(30) + cos(60)` → calculate\n"
        "`x^2 + 2x + 1` → simplify\n"
        "`d/dx x^2` → differentiate\n"
        "`5 + 3 * 2` → calculate\n\n"
        "No commands needed! Just type and get answer.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    result = solve_math(user_input)
    await update.message.reply_text(result, parse_mode="Markdown")

# ---------- Main ----------
def main():
    # Start HTTP server
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Start bot
    print("🤖 Universal Math Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main())

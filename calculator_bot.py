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
        
        # 2. Calculus: d/dx, dy/dx, derivative
        if expr.startswith('d/') or 'derivative' in expr.lower():
            # Parse d/dx x^2 or derivative of x^2
            match = re.search(r'[dD]/[dD][xX]\s*(.+)', expr)
            if match:
                func = match.group(1).strip()
            else:
                func = re.sub(r'(derivative|of)', '', expr, flags=re.IGNORECASE).strip()
            x = sp.Symbol('x')
            f = sp.sympify(func)
            result = sp.diff(f, x)
            return f"📈 *Derivative:*\n`d/dx ({func})`\n= `{result}`"
        
        # 3. Integration: ∫ x^2 dx, integrate x^2
        if expr.startswith('∫') or 'integral' in expr.lower() or 'integrate' in expr.lower():
            match = re.search(r'[∫]?\s*([^dx]+)\s*dx', expr)
            if match:
                func = match.group(1).strip()
            else:
                func = re.sub(r'(integrate|integral|∫)', '', expr, flags=re.IGNORECASE).strip()
            x = sp.Symbol('x')
            f = sp.sympify(func)
            result = sp.integrate(f, x)
            return f"📊 *Integral:*\n`∫ {func} dx`\n= `{result} + C`"
        
        # 4. Trigonometry: sin(30), cos(45), tan(60)
        trig_match = re.match(r'(sin|cos|tan)\((\d+)\)', expr.lower())
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
        
        # 5. Simplify expression: x^2 + 2x + 1
        # Try to simplify first
        f = sp.sympify(expr)
        simplified = sp.simplify(f)
        
        # 6. Factor if possible
        factored = sp.factor(f)
        
        # 7. Expand if needed
        expanded = sp.expand(f)
        
        # Build response
        response = f"🧮 *Expression:* `{expr}`\n\n"
        response += f"🔄 *Simplified:* `{simplified}`\n"
        
        if factored != simplified:
            response += f"🔍 *Factored:* `{factored}`\n"
        if expanded != simplified:
            response += f"📤 *Expanded:* `{expanded}`\n"
        
        # Try to evaluate if it's numeric
        try:
            numeric = float(sp.N(f))
            response += f"🔢 *Value:* `{numeric}`\n"
        except:
            pass
            
        return response
        
    except Exception as e:
        return f"❌ *Error:* {str(e)}\n\n*Try:*\n`3x + 2 = 5`\n`x^2 + 2x + 1`\n`sin(30)`\n`d/dx x^2`"

# ---------- Telegram Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Universal Math Bot* 🧮\n\n"
        "Just type any math expression!\n\n"
        "*Examples:*\n"
        "`3x + 2 = 5` → solve equation\n"
        "`x^2 + 2x + 1` → simplify\n"
        "`d/dx x^2` → differentiate\n"
        "`sin(30)` → trigonometry\n"
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
    main()
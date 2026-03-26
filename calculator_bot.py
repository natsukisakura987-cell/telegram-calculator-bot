from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import math
import re
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import sympy as sp

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

def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Preprocess: convert √ to sqrt, ^ to **
        expr = expr.replace('√', 'sqrt')
        expr = expr.replace('^', '**')
        
        # Convert trig: sin(30) -> sin(30*pi/180) for degrees
        def trig_to_rad(m):
            func = m.group(1)
            deg = int(m.group(2))
            rad = deg * math.pi / 180
            return f"{func}({rad})"
        
        expr = re.sub(r'(sin|cos|tan)\((\d+)\)', trig_to_rad, expr)
        
        # Handle sqrt: sqrt(16) -> sqrt(16)
        # No conversion needed, sympy understands sqrt
        
        # Check if it's an equation
        if '=' in expr:
            left, right = expr.split('=', 1)
            x = sp.Symbol('x')
            
            try:
                # Parse both sides
                left_expr = sp.sympify(left)
                right_expr = sp.sympify(right)
                
                # Create equation and solve
                equation = sp.Eq(left_expr, right_expr)
                solutions = sp.solve(equation, x)
                
                if solutions:
                    # Get first solution
                    sol = solutions[0]
                    
                    # Convert to nice format
                    if sol.is_integer:
                        return f"✅ {original}\n\nx = {int(sol)}"
                    else:
                        # Round to 4 decimal places
                        float_val = float(sol)
                        if abs(float_val - round(float_val, 4)) < 0.0001:
                            float_val = round(float_val, 4)
                        return f"✅ {original}\n\nx = {float_val}"
                else:
                    return f"✅ {original}\n\nx = (could not solve)"
                    
            except Exception as e:
                return f"❌ Error: {str(e)}\n\nTry: 3x+2=5"
        
        # For non-equations, evaluate
        x = sp.Symbol('x')
        result = sp.sympify(expr)
        
        # If result has x, simplify
        if result.has(x):
            simplified = sp.simplify(result)
            return f"✅ {original}\n= {simplified}"
        else:
            # Numeric result
            numeric = float(result)
            if numeric.is_integer():
                numeric = int(numeric)
            else:
                numeric = round(numeric, 6)
            return f"✅ {original}\n= {numeric}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nTry:\n3x+2=5\n2x/3+4=x+2"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any math problem:\n"
        "• 3x+2=5\n"
        "• 2x/3+4=x+2\n"
        "• x/2+3=7\n"
        "• 2x+cos(60)=5\n"
        "• √100+2^3-sin(30)\n\n"
        "Bot by @KanKann_calc_bot"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result)

def main():
    # Start HTTP server
    threading.Thread(target=run_http_server, daemon=True).start()
    
    print("🤖 Bot is starting...")
    
    # Start bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()

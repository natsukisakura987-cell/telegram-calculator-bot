from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import math
import re
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import sympy as sp

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

def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Preprocess: convert √ to sqrt, ^ to **
        expr = expr.replace('√', 'sqrt')
        expr = expr.replace('^', '**')
        
        # Convert trig: sin(30) -> sin(30*pi/180)
        def trig_to_rad(m):
            func = m.group(1)
            deg = float(m.group(2))
            return f"{func}({deg}*pi/180)"
        
        expr = re.sub(r'(sin|cos|tan)\((\d+)\)', trig_to_rad, expr)
        
        # Check if it's an equation
        if '=' in expr:
            left, right = expr.split('=', 1)
            
            # Convert 5x to 5*x for sympy
            left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
            right = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', right)
            
            # Define variable
            x = sp.Symbol('x')
            
            try:
                # Parse both sides
                left_expr = sp.sympify(left)
                right_expr = sp.sympify(right)
                
                # Create equation and solve
                equation = sp.Eq(left_expr, right_expr)
                solutions = sp.solve(equation, x)
                
                if solutions:
                    # Get the first solution
                    sol = solutions[0]
                    
                    # Convert to nice format
                    if sol.is_integer:
                        return f"✅ {original}\n\nx = {int(sol)}"
                    else:
                        # Try to get decimal
                        try:
                            decimal = float(sol)
                            decimal = round(decimal, 6)
                            # Remove trailing zeros
                            if decimal == int(decimal):
                                decimal = int(decimal)
                            return f"✅ {original}\n\nx = {decimal}"
                        except:
                            return f"✅ {original}\n\nx = {sol}"
                else:
                    return f"✅ {original}\n\nx = (could not solve)"
                    
            except Exception as e:
                return f"❌ Error: {str(e)}\n\nTry: 3x+2=5"
        
        # For non-equations, evaluate numerically
        x = sp.Symbol('x')
        expr = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr)
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
        return f"❌ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any equation:\n"
        "• 3x+2=5\n"
        "• 5x+5=34-x\n"
        "• x/3+5=2x-4\n"
        "• 2x/3+4=x+2\n"
        "• x/2+3=7\n\n"
        "Bot by @KanKann_calc_bot"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot is working!")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result)

def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    
    print("🤖 Bot is starting...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()        
        

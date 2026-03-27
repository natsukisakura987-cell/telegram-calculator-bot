from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import math
import re
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

def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Handle √
        expr = expr.replace('√', 'sqrt')
        expr = expr.replace('^', '**')
        
        # Handle trig
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
        
        # Check if it's an equation
        if '=' in expr:
            # Extract left and right
            left, right = expr.split('=')
            
            # First, evaluate the right side if it has no x
            try:
                right_val = eval(right)
            except:
                right_val = None
            
            if right_val is not None:
                # Simple linear equation solver: ax + b = c
                # Convert left to standard form
                left_clean = left.replace(' ', '')
                
                # Find coefficient of x
                if 'x' in left_clean:
                    # Split into parts
                    import re as re_mod
                    
                    # Get coefficient before x
                    match = re_mod.search(r'([+-]?\d*\.?\d*)x', left_clean)
                    if match:
                        coeff_str = match.group(1)
                        if coeff_str == '' or coeff_str == '+':
                            coeff = 1
                        elif coeff_str == '-':
                            coeff = -1
                        else:
                            coeff = float(coeff_str)
                    else:
                        coeff = 0
                    
                    # Get constant term
                    # Remove x term and evaluate remaining
                    remaining = re_mod.sub(r'[+-]?\d*\.?\d*x', '', left_clean)
                    if remaining and remaining != '':
                        if remaining.startswith('+') or remaining.startswith('-'):
                            const = eval(remaining)
                        else:
                            const = eval('+' + remaining) if remaining else 0
                    else:
                        const = 0
                    
                    # Solve: coeff * x + const = right_val
                    # coeff * x = right_val - const
                    # x = (right_val - const) / coeff
                    if coeff != 0:
                        x_solution = (right_val - const) / coeff
                        # Format nicely
                        if abs(x_solution - round(x_solution)) < 0.0001:
                            x_solution = int(round(x_solution))
                        else:
                            x_solution = round(x_solution, 4)
                        return f"✅ {original}\n\nx = {x_solution}"
            
            return f"✅ {original}\n\nx = (could not solve)"
        
        # For non-equations
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"✅ {original}\n= {result}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any math problem:\n"
        "• 3x+2=5\n"
        "• 5x+5=34-x\n"
        "• 2x/3+4=x+2\n"
        "• √16+2\n"
        "• sin(30)+cos(60)"
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

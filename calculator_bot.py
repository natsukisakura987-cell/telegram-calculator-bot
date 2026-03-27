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

def solve_equation(equation):
    """Solve equations like 5x+5=34-x"""
    try:
        # Split into left and right
        left, right = equation.split('=')
        
        # Try to find x by testing values
        solutions = []
        
        # Test x from -100 to 100 with 0.01 increments
        for x_val in range(-10000, 10001):
            x_float = x_val / 100
            
            # Replace x in left and right
            left_test = left.replace('x', str(x_float))
            right_test = right.replace('x', str(x_float))
            
            try:
                # Convert 5x to 5*x for evaluation
                left_test = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left_test)
                right_test = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', right_test)
                
                left_val = eval(left_test)
                right_val = eval(right_test)
                
                if abs(left_val - right_val) < 0.0001:
                    solutions.append(x_float)
                    if len(solutions) > 3:
                        break
            except:
                pass
        
        if solutions:
            # Get the most common solution
            from collections import Counter
            solution = Counter([round(s, 4) for s in solutions]).most_common(1)[0][0]
            if abs(solution - round(solution)) < 0.0001:
                solution = int(round(solution))
            return solution
        return None
    except:
        return None

def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Handle √ symbol
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
        
        # Check if it's an equation (contains = and x)
        if '=' in expr and 'x' in expr:
            solution = solve_equation(expr)
            if solution is not None:
                return f"✅ {original}\n\nx = {solution}"
            else:
                return f"✅ {original}\n\nx = (could not solve)"
        
        # For expressions with x (simplify)
        if 'x' in expr:
            # Convert 5x to 5*x for evaluation
            expr = re.sub(r'(\d+)(x)', r'\1*\2', expr)
            return f"✅ {original}\n= {expr}"
        
        # For regular calculations
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 6)
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
        "• sin(30)+cos(60)\n\n"
        "Bot by @KanKann_calc_bot"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is working!")

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

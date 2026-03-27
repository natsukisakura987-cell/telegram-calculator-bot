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

def evaluate_expression(expr, x_val):
    """Evaluate expression with given x value"""
    try:
        # Replace x with value
        expr_val = expr.replace('x', str(x_val))
        
        # Convert 5x to 5*x
        expr_val = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr_val)
        
        # Handle trig
        def trig_calc(m):
            func = m.group(1)
            deg = float(m.group(2))
            rad = math.radians(deg)
            if func == 'sin':
                return str(round(math.sin(rad), 10))
            if func == 'cos':
                return str(round(math.cos(rad), 10))
            if func == 'tan':
                return str(round(math.tan(rad), 10))
            return m.group(0)
        
        expr_val = re.sub(r'(sin|cos|tan)\((\d+)\)', trig_calc, expr_val)
        
        # Handle sqrt
        def sqrt_calc(m):
            return str(math.sqrt(float(m.group(1))))
        
        expr_val = re.sub(r'sqrt\((\d+)\)', sqrt_calc, expr_val)
        
        # Handle fractions like x/3
        expr_val = expr_val.replace('/', '/')
        
        return eval(expr_val)
    except:
        return None

def solve_equation(equation):
    """Solve linear equation by brute force search"""
    try:
        left, right = equation.split('=')
        
        # Search for x from -100 to 100 with fine steps
        best_x = None
        best_diff = float('inf')
        
        for x_val in range(-10000, 10001):
            x_float = x_val / 100  # 0.01 increments
            
            left_val = evaluate_expression(left, x_float)
            right_val = evaluate_expression(right, x_float)
            
            if left_val is not None and right_val is not None:
                diff = abs(left_val - right_val)
                if diff < 0.0001:
                    # Exact match found
                    solution = x_float
                    if abs(solution - round(solution)) < 0.0001:
                        solution = int(round(solution))
                    else:
                        solution = round(solution, 4)
                    return solution
                if diff < best_diff:
                    best_diff = diff
                    best_x = x_float
        
        # If no exact match but close enough
        if best_x is not None and best_diff < 0.01:
            solution = best_x
            if abs(solution - round(solution)) < 0.0001:
                solution = int(round(solution))
            else:
                solution = round(solution, 4)
            return solution
        
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Handle √
        expr = expr.replace('√', 'sqrt')
        expr = expr.replace('^', '**')
        
        # Check if it's an equation
        if '=' in expr:
            solution = solve_equation(expr)
            if solution is not None:
                return f"✅ {original}\n\nx = {solution}"
            else:
                return f"✅ {original}\n\nx = (could not solve)"
        
        # For non-equations
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
        
        # Add multiplication for numbers and variables
        expr = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr)
        
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"✅ {original}\n= {result}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any equation:\n"
        "• 3x+2=5 → x=1\n"
        "• 5x+5=34-x → x=4.8333\n"
        "• x/3+5=2x-4 → x=5.4\n"
        "• 2x/3+4=x+2 → x=6\n"
        "• x/2+3=7 → x=8\n\n"
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

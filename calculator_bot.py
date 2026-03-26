from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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

def solve_equation(equation):
    """Solve equations like 2x/3+4=x+2"""
    try:
        # Split into left and right
        left, right = equation.split('=')
        
        # Function to evaluate expression for a given x
        def evaluate(expr, x_val):
            # Replace x with value
            expr_val = expr.replace('x', f'({x_val})')
            # Handle fractions like 2x/3
            expr_val = expr_val.replace('/', '/')
            try:
                return eval(expr_val)
            except:
                return None
        
        # Find solution by binary search
        # First, find a range where left - right changes sign
        step = 1
        found_range = False
        lower_bound = -100
        upper_bound = 100
        lower_val = evaluate(left, lower_bound) - evaluate(right, lower_bound)
        
        if lower_val is None:
            return None
        
        for x_test in range(-100, 101):
            x_val = x_test
            diff = evaluate(left, x_val) - evaluate(right, x_val)
            if diff is None:
                continue
            if diff * lower_val < 0:  # Sign change found
                found_range = True
                upper_bound = x_val
                break
            lower_val = diff
            lower_bound = x_val
        
        if not found_range:
            # Try with more precision
            for x_test in range(-1000, 1001):
                x_val = x_test / 10
                diff = evaluate(left, x_val) - evaluate(right, x_val)
                if diff is None:
                    continue
                if abs(diff) < 0.0001:
                    return x_val
                if diff * lower_val < 0:
                    found_range = True
                    upper_bound = x_val
                    break
                lower_val = diff
                lower_bound = x_val
        
        if found_range:
            # Binary search for exact solution
            for _ in range(50):  # 50 iterations for precision
                mid = (lower_bound + upper_bound) / 2
                diff = evaluate(left, mid) - evaluate(right, mid)
                if diff is None:
                    break
                if abs(diff) < 0.0001:
                    return mid
                if diff * (evaluate(left, lower_bound) - evaluate(right, lower_bound)) > 0:
                    lower_bound = mid
                else:
                    upper_bound = mid
            return (lower_bound + upper_bound) / 2
        
        return None
        
    except Exception as e:
        return None

def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Handle special symbols
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
        
        # Replace trig with values
        expr = re.sub(r'(sin|cos|tan)\((\d+)\)', trig_calc, expr)
        
        # Handle sqrt
        def sqrt_calc(m):
            num = float(m.group(1))
            return str(math.sqrt(num))
        
        expr = re.sub(r'sqrt\((\d+)\)', sqrt_calc, expr)
        
        # Check if it's an equation
        if '=' in expr:
            # Solve the equation
            solution = solve_equation(expr)
            
            if solution is not None:
                # Format the solution nicely
                if abs(solution - round(solution)) < 0.0001:
                    solution = int(round(solution))
                else:
                    solution = round(solution, 4)
                return f"✅ {original}\n\nx = {solution}"
            else:
                return f"✅ {original}\n\nx = (could not solve)"
        
        # For non-equations, just calculate
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"✅ {original}\n= {result}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nTry:\n3x+2=5\n2x/3+4=x+2\nx/2+3=7"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any math problem:\n"
        "• 3x+2=5\n"
        "• 2x/3+4=x+2\n"
        "• x/2+3=7\n"
        "• 2x+cos(60)=5\n"
        "• √100+2^3-sin(30)"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result)

def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    
    print("🤖 Bot is starting...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()

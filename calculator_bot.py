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

def solve_linear_equation(equation):
    """Solve linear equation like x/3+5=2x-4, 5x+5=34-x, etc."""
    try:
        # Split into left and right
        left, right = equation.split('=')
        
        # Remove all spaces
        left = left.replace(' ', '')
        right = right.replace(' ', '')
        
        # Evaluate right side if it has no x
        if 'x' not in right:
            right_value = eval(right)
        else:
            right_value = None
        
        # For equations with x on both sides, we'll use brute force
        # Test x values from -100 to 100 with high precision
        solutions = []
        
        for x_val in range(-10000, 10001):
            x_float = x_val / 100  # 0.01 increments
            
            # Replace x in left and right
            left_test = left.replace('x', f'({x_float})')
            right_test = right.replace('x', f'({x_float})')
            
            # Convert 5x to 5*x for evaluation
            left_test = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left_test)
            right_test = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', right_test)
            
            # Handle trig
            def trig_calc(m):
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
            
            left_test = re.sub(r'(sin|cos|tan)\((\d+)\)', trig_calc, left_test)
            right_test = re.sub(r'(sin|cos|tan)\((\d+)\)', trig_calc, right_test)
            
            # Handle sqrt
            def sqrt_calc(m):
                return str(math.sqrt(float(m.group(1))))
            
            left_test = re.sub(r'sqrt\((\d+)\)', sqrt_calc, left_test)
            right_test = re.sub(r'sqrt\((\d+)\)', sqrt_calc, right_test)
            
            # Handle fractions like x/3
            try:
                left_val = eval(left_test)
                right_val = eval(right_test)
                
                if abs(left_val - right_val) < 0.0001:
                    solutions.append(x_float)
                    if len(solutions) > 5:
                        break
            except:
                pass
        
        if solutions:
            # Average solutions if multiple (should be same value)
            solution = sum(solutions) / len(solutions)
            # Round to 4 decimal places
            solution = round(solution, 4)
            # If integer, show as integer
            if solution == int(solution):
                solution = int(solution)
            return solution
        else:
            return None
            
    except Exception as e:
        print(f"Error in solve_linear_equation: {e}")
        return None

def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Handle special symbols first
        expr = expr.replace('√', 'sqrt')
        expr = expr.replace('^', '**')
        
        # Check if it's an equation
        if '=' in expr:
            solution = solve_linear_equation(expr)
            if solution is not None:
                return f"✅ {original}\n\nx = {solution}"
            else:
                return f"✅ {original}\n\nx = (could not solve)"
        
        # For non-equations (calculations)
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
        
        # Handle multiplication: 5x -> 5*x
        expr = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr)
        
        # Evaluate
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
        "🧮 *Math Bot*\n\n"
        "Type any equation or calculation:\n\n"
        "*Equations:*\n"
        "• `3x+2=5` → x = 1\n"
        "• `5x+5=34-x` → x = 4.8333\n"
        "• `x/3+5=2x-4` → x = 5.4\n"
        "• `2x/3+4=x+2` → x = 6\n\n"
        "*Calculations:*\n"
        "• `√16+2` → 6\n"
        "• `sin(30)+cos(60)` → 1\n"
        "• `2^3+4` → 12\n\n"
        "Bot by @KanKann_calc_bot",
        parse_mode="Markdown"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot is working!")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result, parse_mode="Markdown")

def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    
    print("🤖 Bot is starting...")
    print("Ready to solve equations!")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()

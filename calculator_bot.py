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
    """Solve linear equations with fractions, decimals, x on both sides"""
    try:
        # Split into left and right
        left, right = equation.split('=')
        
        # Function to convert expression to a standard form: ax + b
        def to_standard_form(expr):
            # Replace √ and ^
            expr = expr.replace('√', 'sqrt')
            expr = expr.replace('^', '**')
            
            # Handle trig functions
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
            
            expr = re.sub(r'(sin|cos|tan)\((\d+)\)', trig_calc, expr)
            
            # Handle sqrt
            def sqrt_calc(m):
                return str(math.sqrt(float(m.group(1))))
            
            expr = re.sub(r'sqrt\((\d+)\)', sqrt_calc, expr)
            
            # Replace x with a placeholder to evaluate constants
            # We'll use brute force to find coefficient and constant
            # Method: Evaluate at x=0 and x=1 to get constants
            try:
                # At x = 0, we get the constant term
                expr_at_0 = expr.replace('x', '0')
                expr_at_0 = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr_at_0)
                const = eval(expr_at_0)
                
                # At x = 1, we get coefficient + constant
                expr_at_1 = expr.replace('x', '1')
                expr_at_1 = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr_at_1)
                val_at_1 = eval(expr_at_1)
                
                # Coefficient = (value at 1) - (value at 0)
                coeff = val_at_1 - const
                
                return coeff, const
            except:
                # Fallback: brute force to find coefficient
                for x_val in range(-1000, 1001):
                    x_float = x_val / 100
                    expr_at_x = expr.replace('x', str(x_float))
                    expr_at_x = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr_at_x)
                    try:
                        # Try to find pattern
                        pass
                    except:
                        pass
                return None, None
        
        # Parse both sides
        left_coeff, left_const = to_standard_form(left)
        right_coeff, right_const = to_standard_form(right)
        
        if left_coeff is not None and right_coeff is not None:
            # Solve: left_coeff * x + left_const = right_coeff * x + right_const
            # (left_coeff - right_coeff) * x = right_const - left_const
            coeff_diff = left_coeff - right_coeff
            const_diff = right_const - left_const
            
            if abs(coeff_diff) > 0.0001:
                solution = const_diff / coeff_diff
                # Format nicely
                if abs(solution - round(solution)) < 0.0001:
                    solution = int(round(solution))
                else:
                    solution = round(solution, 4)
                return solution
        
        # Fallback: brute force search
        left_expr = left
        right_expr = right
        
        for x_val in range(-10000, 10001):
            x_float = x_val / 100
            test_left = left_expr.replace('x', str(x_float))
            test_right = right_expr.replace('x', str(x_float))
            test_left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', test_left)
            test_right = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', test_right)
            
            try:
                left_val = eval(test_left)
                right_val = eval(test_right)
                if abs(left_val - right_val) < 0.0001:
                    solution = x_float
                    if abs(solution - round(solution)) < 0.0001:
                        solution = int(round(solution))
                    else:
                        solution = round(solution, 4)
                    return solution
            except:
                pass
        
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
        # Handle trig first
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
        "• 3x+2=5\n"
        "• 5x+5=34-x\n"
        "• x/3+5=2x-4\n"
        "• 2x/3+4=x+2\n"
        "• 3x+√16=2x+8\n"
        "• 2x+sin(30)=5\n\n"
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

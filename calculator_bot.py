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
    """Solve linear equations with x on both sides"""
    try:
        # Split into left and right
        left, right = equation.split('=')
        
        # Clean up spaces
        left = left.replace(' ', '')
        right = right.replace(' ', '')
        
        # Function to extract coefficient of x and constant
        def parse_side(side):
            # Replace 'x' with '*x' for evaluation
            side = re.sub(r'(\d+)(x)', r'\1*\2', side)
            
            # Find coefficient of x
            if 'x' in side:
                # Find x term
                x_match = re.search(r'([+-]?\d*\.?\d*)\*?x', side)
                if x_match:
                    coeff_str = x_match.group(1)
                    if coeff_str == '' or coeff_str == '+':
                        coeff = 1
                    elif coeff_str == '-':
                        coeff = -1
                    else:
                        coeff = float(coeff_str)
                else:
                    coeff = 0
                
                # Remove x term to get constant
                without_x = re.sub(r'[+-]?\d*\.?\d*\*?x', '', side)
                if without_x and without_x != '':
                    if without_x.startswith('+') or without_x.startswith('-'):
                        const = eval(without_x) if without_x else 0
                    else:
                        const = eval('+' + without_x) if without_x else 0
                else:
                    const = 0
            else:
                coeff = 0
                const = eval(side) if side else 0
            
            return coeff, const
        
        # Parse both sides
        left_coeff, left_const = parse_side(left)
        right_coeff, right_const = parse_side(right)
        
        # Solve: left_coeff * x + left_const = right_coeff * x + right_const
        # (left_coeff - right_coeff) * x = right_const - left_const
        # x = (right_const - left_const) / (left_coeff - right_coeff)
        
        coeff_diff = left_coeff - right_coeff
        const_diff = right_const - left_const
        
        if coeff_diff != 0:
            solution = const_diff / coeff_diff
            # Format nicely
            if abs(solution - round(solution)) < 0.0001:
                solution = int(round(solution))
            else:
                solution = round(solution, 4)
            return solution
        
        return None
    except Exception as e:
        print(f"Error parsing equation: {e}")
        return None

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
            # First, try to solve with algebraic method
            solution = solve_equation(expr)
            if solution is not None:
                return f"✅ {original}\n\nx = {solution}"
            
            # Fallback: brute force method
            left, right = expr.split('=')
            try:
                right_val = eval(right)
            except:
                right_val = None
            
            if right_val is not None:
                for x_val in range(-1000, 1001):
                    x_float = x_val / 10
                    test_left = left.replace('x', str(x_float))
                    test_left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', test_left)
                    try:
                        if abs(eval(test_left) - right_val) < 0.0001:
                            result = int(x_float) if x_float.is_integer() else round(x_float, 4)
                            return f"✅ {original}\n\nx = {result}"
                    except:
                        pass
            
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
        "• 2x+3=x+7\n"
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

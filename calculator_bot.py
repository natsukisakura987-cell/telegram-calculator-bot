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

def solve_math(expr):
    try:
        expr = expr.strip()
        original = expr
        
        # Convert √ to sqrt()
        expr = re.sub(r'√(\d+)', r'sqrt(\1)', expr)
        expr = re.sub(r'√(\d+\.\d+)', r'sqrt(\1)', expr)
        
        # Convert ^ to **
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
            num = float(m.group(1))
            return str(math.sqrt(num))
        
        expr = re.sub(r'sqrt\((\d+)\)', sqrt_calc, expr)
        
        # Add multiplication: 2x -> 2*x
        expr = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr)
        
        # Handle equations with variables on both sides
        if '=' in expr:
            parts = expr.split('=')
            left = parts[0]
            right = parts[1]
            
            try:
                # Check if x appears on both sides
                if 'x' in left and 'x' in right:
                    # Move all x terms to left, constants to right
                    # For equation: ax + b = cx + d
                    # (a - c)x = d - b
                    # x = (d - b) / (a - c)
                    
                    # Extract coefficient of x on left
                    import re as re_module
                    
                    def get_coeff_and_const(expression):
                        expr = expression.replace(' ', '')
                        coeff = 0
                        const = 0
                        
                        # Find x term
                        x_match = re_module.search(r'([+-]?\d*\.?\d*)\*?x', expr)
                        if x_match:
                            coeff_str = x_match.group(1)
                            if coeff_str == '' or coeff_str == '+':
                                coeff = 1
                            elif coeff_str == '-':
                                coeff = -1
                            else:
                                coeff = float(coeff_str)
                            # Remove x term from expression
                            expr = re_module.sub(r'[+-]?\d*\.?\d*\*?x', '', expr, count=1)
                        
                        # Evaluate remaining constant
                        if expr and expr != '':
                            # Handle multiple terms
                            expr = expr.replace('--', '+')
                            expr = expr.replace('+-', '-')
                            if expr:
                                const = eval(expr)
                        
                        return coeff, const
                    
                    a, b = get_coeff_and_const(left)
                    c, d = get_coeff_and_const(right)
                    
                    # Solve (a - c)x = d - b
                    x_solution = (d - b) / (a - c)
                    
                    # Format nicely
                    if abs(x_solution - round(x_solution, 4)) < 0.0001:
                        x_solution = round(x_solution, 4)
                    if isinstance(x_solution, float) and x_solution.is_integer():
                        x_solution = int(x_solution)
                    
                    return f"✅ {original}\n\nx = {x_solution}"
                
                # Simple equation with x only on one side
                else:
                    right_val = eval(right)
                    left = left.replace(' ', '')
                    
                    import re as re_module
                    match = re_module.match(r'([+-]?\d*\.?\d*)\*?x([+-].*)?', left)
                    if match:
                        coeff_str = match.group(1)
                        if coeff_str == '' or coeff_str == '+':
                            coeff = 1
                        elif coeff_str == '-':
                            coeff = -1
                        else:
                            coeff = float(coeff_str)
                        
                        rest = match.group(2) if match.group(2) else ''
                        if rest:
                            const = eval(rest)
                        else:
                            const = 0
                        
                        x_solution = (right_val - const) / coeff
                        
                        if abs(x_solution - round(x_solution, 4)) < 0.0001:
                            x_solution = round(x_solution, 4)
                        if isinstance(x_solution, float) and x_solution.is_integer():
                            x_solution = int(x_solution)
                        
                        return f"✅ {original}\n\nx = {x_solution}"
                        
            except Exception as e:
                pass
            
            # Fallback brute force
            solutions = []
            for x_val in range(-1000, 1001):
                x_float = x_val / 10
                test_left = left.replace('x', str(x_float))
                test_right = right.replace('x', str(x_float))
                try:
                    left_val = eval(test_left)
                    right_val = eval(test_right)
                    if abs(left_val - right_val) < 0.0001:
                        solutions.append(x_float)
                except:
                    pass
            
            if solutions:
                solutions = sorted(list(set([round(s, 4) for s in solutions])))
                if len(solutions) == 1:
                    return f"✅ {original}\n\nx = {solutions[0]}"
                else:
                    return f"✅ {original}\n\nx = {solutions}"
            else:
                return f"✅ {original}\n\nx = (could not solve)"
        
        # Calculate result for non-equation expressions
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"✅ {original}\n= {result}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nTry:\n3x+2=5\n5x+5=34-x\n√16+2"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any math problem:\n"
        "• 3x+2=5\n"
        "• 5x+5=34-x\n"
        "• 2x+cos(60)=5\n"
        "• √100+2^3-sin(30)\n"
        "• sin(30)+cos(60)"
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

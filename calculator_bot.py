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
        
        # Handle equations
        if '=' in expr:
            parts = expr.split('=')
            left = parts[0]
            right = parts[1]
            
            try:
                # Evaluate right side first (might contain trig, sqrt, etc.)
                right_val = eval(right)
                
                # For equations like x/2+3=7, we need to solve for x
                # Create a function that solves by isolating x
                
                # Try different x values to find solution (brute force with high precision)
                solutions = []
                # Test decimal values from -100 to 100 with 0.01 increments
                for x_val in range(-10000, 10001):
                    x_float = x_val / 100  # 0.01 increments
                    test_left = left.replace('x', str(x_float))
                    try:
                        left_val = eval(test_left)
                        if abs(left_val - right_val) < 0.0001:
                            solutions.append(round(x_float, 4))
                    except:
                        pass
                
                if solutions:
                    # Remove duplicates and sort
                    solutions = sorted(list(set(solutions)))
                    if len(solutions) == 1:
                        x_result = solutions[0]
                        # Format nicely
                        if abs(x_result - round(x_result)) < 0.0001:
                            x_result = int(round(x_result))
                        elif abs(x_result - round(x_result, 2)) < 0.0001:
                            x_result = round(x_result, 2)
                        else:
                            x_result = round(x_result, 4)
                        return f"✅ {original}\n\nx = {x_result}"
                    else:
                        return f"✅ {original}\n\nx = {solutions}"
                else:
                    return f"✅ {original}\n\nx = (could not solve)"
                        
            except Exception as e:
                return f"❌ Error solving: {str(e)}"
        
        # Calculate result for non-equation expressions
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"✅ {original}\n= {result}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nTry:\n3x+2=5\nx/2+3=7\n√16+2"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any math problem:\n"
        "• 3x+2=5\n"
        "• 5x+5=34-x\n"
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

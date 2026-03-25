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
        
        # Handle √ symbol
        expr = expr.replace('√', 'sqrt')
        expr = re.sub(r'sqrt(\d+)', r'sqrt(\1)', expr)
        
        # Handle ^ for power
        expr = expr.replace('^', '**')
        
        # Add multiplication: 2x -> 2*x
        expr = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr)
        
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
        
        # Solve equations
        if '=' in expr:
            parts = expr.split('=')
            left = parts[0]
            right = parts[1]
            
            # Simple linear equation solver
            for x_val in range(-100, 101):
                test_left = left.replace('x', str(x_val))
                test_right = right.replace('x', str(x_val))
                try:
                    left_val = eval(test_left)
                    right_val = eval(test_right)
                    if abs(left_val - right_val) < 0.0001:
                        return f"✅ {expr}\n\nx = {x_val}"
                except:
                    pass
            return f"✅ {expr}\n\nx = (could not solve)"
        
        # Evaluate regular expression
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"✅ {expr}\n= {result}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any math problem:\n"
        "• 3x+2=5\n"
        "• √16+2\n"
        "• sin(30)+cos(60)\n"
        "• 2^3+4"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result)

def main():
    # Start HTTP server
    thread = threading.Thread(target=run_http_server, daemon=True)
    thread.start()
    
    print("🤖 Bot is starting...")
    
    # Start bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()from telegram import Update
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
        
        # Handle √ symbol
        expr = expr.replace('√', 'sqrt')
        expr = re.sub(r'sqrt(\d+)', r'sqrt(\1)', expr)
        
        # Handle ^ for power
        expr = expr.replace('^', '**')
        
        # Add multiplication: 2x -> 2*x
        expr = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr)
        
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
        
        # Solve equations
        if '=' in expr:
            parts = expr.split('=')
            left = parts[0]
            right = parts[1]
            
            # Simple linear equation solver
            for x_val in range(-100, 101):
                test_left = left.replace('x', str(x_val))
                test_right = right.replace('x', str(x_val))
                try:
                    left_val = eval(test_left)
                    right_val = eval(test_right)
                    if abs(left_val - right_val) < 0.0001:
                        return f"✅ {expr}\n\nx = {x_val}"
                except:
                    pass
            return f"✅ {expr}\n\nx = (could not solve)"
        
        # Evaluate regular expression
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"✅ {expr}\n= {result}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Math Bot\n\n"
        "Type any math problem:\n"
        "• 3x+2=5\n"
        "• √16+2\n"
        "• sin(30)+cos(60)\n"
        "• 2^3+4"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = solve_math(update.message.text)
    await update.message.reply_text(result)

def main():
    # Start HTTP server
    thread = threading.Thread(target=run_http_server, daemon=True)
    thread.start()
    
    print("🤖 Bot is starting...")
    
    # Start bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_polling()

if __name__ == "__main__":
    main()

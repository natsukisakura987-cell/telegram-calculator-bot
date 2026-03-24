from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sympy as sp
import math
import re
import asyncio
import os

TOKEN = "8417018128:AAHAm_2-OP22yzWv3VFPvOGT6-HTNgmspT4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Advanced Math Bot* 🧮\n\n"
        "I can solve various math problems!\n\n"
        "*📐 Trigonometry:*\n"
        "`sin(30)`, `cos(45)`, `tan(60)`\n\n"
        "*📊 Calculus:*\n"
        "`differentiate x^2`\n"
        "`integrate 2x`\n\n"
        "*🔢 Algebra:*\n"
        "`solve x^2 - 4 = 0`\n"
        "`simplify (x+1)^2`\n\n"
        "*➕ Basic Math:*\n"
        "`5 + 3`, `10 * 2`, `(4+6)/2`\n\n"
        "Just type your math problem!",
        parse_mode="Markdown"
    )

def solve_math_problem(query):
    try:
        query = query.lower().strip()
        
        # Calculus: Differentiate
        if 'differentiate' in query or 'derivative' in query or 'diff' in query:
            expr_str = re.sub(r'(differentiate|derivative|diff)', '', query).strip()
            x = sp.Symbol('x')
            expr = sp.sympify(expr_str)
            result = sp.diff(expr, x)
            return f"📈 *Derivative:*\n`d/dx ({expr_str})`\n= `{result}`"
        
        # Calculus: Integrate
        elif 'integrate' in query or 'integral' in query or 'int' in query:
            expr_str = re.sub(r'(integrate|integral|int)', '', query).strip()
            x = sp.Symbol('x')
            expr = sp.sympify(expr_str)
            result = sp.integrate(expr, x)
            return f"📊 *Integral:*\n`∫ {expr_str} dx`\n= `{result} + C`"
        
        # Algebra: Solve equations
        elif 'solve' in query:
            equation = re.sub(r'solve', '', query).strip()
            x = sp.Symbol('x')
            result = sp.solve(equation, x)
            return f"🔢 *Solution:*\n`{equation}`\n= `{result}`"
        
        # Simplify expressions
        elif 'simplify' in query:
            expr_str = re.sub(r'simplify', '', query).strip()
            expr = sp.sympify(expr_str)
            result = sp.simplify(expr)
            return f"🔄 *Simplified:*\n`{expr_str}`\n= `{result}`"
        
        # Factor expressions
        elif 'factor' in query:
            expr_str = re.sub(r'factor', '', query).strip()
            expr = sp.sympify(expr_str)
            result = sp.factor(expr)
            return f"🔍 *Factored:*\n`{expr_str}`\n= `{result}`"
        
        # Expand expressions
        elif 'expand' in query:
            expr_str = re.sub(r'expand', '', query).strip()
            expr = sp.sympify(expr_str)
            result = sp.expand(expr)
            return f"📤 *Expanded:*\n`{expr_str}`\n= `{result}`"
        
        # Trigonometry with degrees
        elif any(trig in query for trig in ['sin', 'cos', 'tan']):
            match = re.search(r'(sin|cos|tan)\((\d+)\)', query)
            if match:
                func = match.group(1)
                angle = float(match.group(2))
                rad = math.radians(angle)
                if func == 'sin':
                    result = math.sin(rad)
                elif func == 'cos':
                    result = math.cos(rad)
                else:
                    result = math.tan(rad)
                return f"📐 *{func}({angle}°)*\n= `{result:.6f}`"
        
        # Basic arithmetic
        else:
            allowed = "0123456789+-*/(). "
            if all(c in allowed or c.isspace() for c in query):
                result = eval(query)
                return f"✅ *Result:*\n`{query}`\n= `{result}`"
            else:
                return ("❌ *I couldn't understand your query*\n\n"
                       "*Try these commands:*\n"
                       "`differentiate x^2`\n"
                       "`integrate 2x`\n"
                       "`solve x^2 - 4 = 0`\n"
                       "`sin(30)`\n"
                       "`5 + 3`")
    
    except Exception as e:
        return f"❌ *Error:* {str(e)}"

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    result = solve_math_problem(user_input)
    await update.message.reply_text(result, parse_mode="Markdown")

def main():
    print("🤖 Advanced Math Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))
    
    # Use run_polling with the correct event loop handling for Render
    app.run_polling()

if __name__ == "__main__":
    main()

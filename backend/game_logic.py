import requests
import google.generativeai as genai
import sqlite3
import random
import yfinance as yf
from dotenv import load_dotenv
#from blockchain import store_transaction

load_dotenv()

genai.configure(api_key="AIzaSyAszRUnBNw2Q2GD9T0X737QE9agf-WDWJQ")
consecutive_wins = {}
consecutive_losses = {}

def generate_financial_advice():
    """Using Gemini AI to fetch top 10 recommended stocks."""
    response = genai.GenerativeModel('gemini-pro').generate_content("List 10 trending stocks for investment.")
    return response.text.split("\n")[:10]

def get_real_time_stock_price(symbol):
    """Fetching real-time stock price from yFinance API."""
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    return data['Close'].iloc[-1]

def process_investment(user_id, stock_symbol, amount):
    """The logic of stock investment and applies game rules (level up, punishment, rewards)."""
    
    global consecutive_wins, consecutive_losses
    
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()

    cursor.execute("SELECT balance, level FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        return {"error": "User not found"}

    balance, level = user

    if balance < amount:
        return {"error": "Insufficient funds"}

    # Fetch real-time stock price
    try:
        stock_price = get_real_time_stock_price(stock_symbol)
    except Exception as e:
        return {"error": f"Failed to fetch stock data: {str(e)}"}

    # Simulate investment outcome (random multiplier)
    multiplier = random.choice([2,3,4,5,6,7,8,9,10])  # Loss or profit
    outcome = amount * multiplier

    new_balance = balance + outcome - amount

    # Store transaction in database
    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
    cursor.execute("INSERT INTO transactions (user_id, stock_symbol, investment, outcome) VALUES (?, ?, ?, ?)", 
                   (user_id, stock_symbol, amount, outcome))

    # Store transaction in Midnight blockchain
    #store_transaction(user_id, stock_symbol, amount, outcome)

    message = ""
    
    # Check Level Up Condition
    if new_balance >= balance * 2 and level == 1:
        level = 2
        cursor.execute("UPDATE users SET level = ? WHERE id = ?", (level, user_id))
        message = "🎉 Congratulations! You've leveled up to Level 2!"
    elif new_balance >= balance * 3 and level == 2:
        level = 3
        cursor.execute("UPDATE users SET level = ? WHERE id = ?", (level, user_id))
        message = "🚀 You are now at Level 3! Keep going!"

    # Game Over Condition
    if new_balance < 0:
        message = "💀 Game Over! You went bankrupt!"
        cursor.execute("UPDATE users SET balance = 10000, level = 1 WHERE id = ?", (user_id,))  # Reset Game
        new_balance = 10000
        level = 1
        consecutive_wins[user_id] = 0
        consecutive_losses[user_id] = 0
    else:
        # Track win/loss streak
        if outcome > 0:
            consecutive_wins[user_id] = consecutive_wins.get(user_id, 0) + 1
            consecutive_losses[user_id] = 0
        else:
            consecutive_losses[user_id] = consecutive_losses.get(user_id, 0) + 1
            consecutive_wins[user_id] = 0

        # Apply Reward for Consecutive Wins
        if consecutive_wins[user_id] >= 2:
            new_balance += 100
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
            message += " 🎁 Bonus! You got a $100 reward for 2 consecutive wins!"
            consecutive_wins[user_id] = 0  # Reset streak

        # Apply Punishment for Consecutive Losses
        if consecutive_losses[user_id] >= 3 and level > 1:
            level -= 1
            cursor.execute("UPDATE users SET level = ? WHERE id = ?", (level, user_id))
            message += " ⛔ You lost 3 times in a row. You have been demoted to the previous level!"
            consecutive_losses[user_id] = 0  # Reset streak

    conn.commit()
    conn.close()

    return {"new_balance": new_balance, "level": level, "message": message}

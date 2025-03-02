import os
import random
import sqlite3
import google.generativeai as genai
from stocks import get_real_time_stock_price, get_historical_percentage_change
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

def get_gemini_stock_recommendations():
    """Fetch 10 trending stocks with structured financial advice from Gemini AI."""
    prompt = """
    You are providing virtual stock investment recommendations in a stock simulation game.
    Provide 10 trending stock symbols along with investment advice and a suggested percentage to invest (between 5% and 25%). 
    Format the response strictly as follows:
    
    SYMBOL - Advice - Percentage_to_Invest
    Example:
    AAPL - Apple's stock is stable with long-term growth potential - 15%
    TSLA - Tesla's stock is volatile, consider short-term trading - 10%
    
    Only provide 10 recommendations and avoid disclaimers or generic investment warnings.
    """

    response = genai.GenerativeModel('gemini-2.0-flash').generate_content(prompt)

    stock_list = response.text.split("\n")[:10]
    recommendations = []

    for stock in stock_list:
        parts = stock.split(" - ")
        if len(parts) == 3:
            symbol, advice, percentage = parts
            try:
                percentage = float(percentage.replace("%", "").strip())  # Convert percentage to float
            except ValueError:
                percentage = random.uniform(50, 100)  # Assign a random percentage if parsing fails
            recommendations.append({
                "symbol": symbol.strip(),
                "advice": advice.strip(),
                "priority": percentage
            })

    return recommendations

def calculate_investment_return(investment_amount, symbol, days=1):
    """Calculating return on investment based on historical data with market simulation."""
    historical_change = get_historical_percentage_change(symbol)
    
    if historical_change is None:
        return None, None

    return_amount = (investment_amount * historical_change) / 100

    # Multiply by a random factor (1 to 10) to simulate the result
    random_factor = random.randint(1, 10)
    total_return = return_amount * random_factor

    # Convert to scalar value
    total_return = float(total_return)

    # Determine profit or loss
    profit_or_loss = "profit" if total_return > 0 else "loss"

    # Display message based on the result
    if profit_or_loss == "profit":
        message = f"🎉 Hurray! You've made a profit of ${total_return:.2f}!"
    else:
        message = f"💸 Oops! You've made a loss of ${-total_return:.2f}. Better luck next time!"

    return total_return, profit_or_loss, message

def process_investment(user_id, stock_symbol, amount):
    """The logic of stock investment and applies game rules (level up, punishment, rewards)."""
    
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()

    cursor.execute("SELECT balance, level, consecutive_wins, consecutive_losses FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        return {"error": "User not found"}

    balance, level, consecutive_wins, consecutive_losses = user

    if balance < amount:
        return {"error": "Oops! Insufficient funds"}

    # Get the real-time price for the stock
    current_price = get_real_time_stock_price(stock_symbol)
    if current_price is None:
        return {"error": "Failed to fetch real-time stock price."}

    # Ensure current_price is a scalar value (float)
    current_price = float(current_price)

    # Calculate the investment return based on historical data and real-time data
    investment_return, profit_or_loss, message = calculate_investment_return(amount, stock_symbol, 1)

    if investment_return is None:
        return {"error": "Stock data unavailable"}

    new_balance = balance + investment_return
    roi = investment_return

    # Record the transaction in the database
    cursor.execute("""
        INSERT INTO TRANSACTIONS (user_id, stock_symbol, invested_amount, current_value, return_amount, profit_loss, return_on_investment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, stock_symbol, amount, current_price, investment_return, profit_or_loss, roi))

    # Handle consecutive wins/losses
    if profit_or_loss == "profit":
        consecutive_wins += 1
        consecutive_losses = 0
    else:
        consecutive_losses += 1
        consecutive_wins = 0

    # Reward or Punishment
    if consecutive_wins >= 3:
        new_balance += 100  # Reward of $100 for 3 consecutive wins
        message += " 🎁 Bonus! You got a $100 reward for 3 consecutive wins! Keep going Trader 🚀"
        consecutive_wins = 0

    if consecutive_losses >= 3 and level >= 1:
        if level > 1:
          level -= 1  # Demote if 3 consecutive losses
          message += " ⛔ You lost 3 times in a row. You have been demoted to the previous level!"
          consecutive_losses = 0
        if level == 1:
            new_balance -=100
            message += " 💸 You lost 3 times in a row. You have been fined $100! Please focus on good investments"
            consecutive_losses = 0
          
          

    # Level up if balance doubles
    if new_balance > balance * 2:
        level += 1
        cursor.execute("UPDATE users SET level = ? WHERE id = ?", (level, user_id))
        message += " 🎉 Congratulations! You've leveled up to Level" + level +"!"

    # Level up to Level 3 if balance triples
    elif new_balance > balance * 3 and level == 2:
        level = 3
        cursor.execute("UPDATE users SET level = ? WHERE id = ?", (level, user_id))
        message += " 🚀 You are now at Level 3! Keep going!"

    # Game Over if balance goes negative
    if new_balance < 0:
        message = "💀 Game Over! You are bankrupt."
        cursor.execute("UPDATE users SET balance = 10000, level = 1 WHERE id = ?", (user_id,))
        new_balance = 10000
        level = 1
        consecutive_wins = 0
        consecutive_losses = 0

    cursor.execute("""
        UPDATE users SET balance = ?, level = ?, consecutive_wins = ?, consecutive_losses = ? WHERE id = ?
    """, (new_balance, level, consecutive_wins, consecutive_losses, user_id))

    conn.commit()
    conn.close()

    return {
        "new_balance": new_balance,
        "level": level,
        "profit_or_loss": profit_or_loss,
        "roi": roi,
        "message": message
    }

import sqlite3
from game_logic import process_investment, get_gemini_stock_recommendations, calculate_investment_return

def test_process_investment():
    # Simulate user data
    user_id = 1  # You can change this to the appropriate user ID in your database
    stock_symbol = 'AAPL'  # Simulated stock symbol (Apple)
    amount = 1000  # Simulated investment amount

    # Call the process_investment function
    result = process_investment(user_id, stock_symbol, amount)

    print("Test result: ")
    print(result)

def test_get_gemini_stock_recommendations():
    # Get the stock recommendations from Gemini AI
    recommendations = get_gemini_stock_recommendations()
    
    print("Gemini Stock Recommendations: ")
    for recommendation in recommendations:
        print(f"Stock: {recommendation['symbol']}, Advice: {recommendation['advice']}, Priority: {recommendation['priority']}")

def test_calculate_investment_return():
    stock_symbol = 'AAPL'  # Stock symbol
    amount = 1000  # Investment amount

    # Calculate the return
    investment_return, profit_or_loss = calculate_investment_return(amount, stock_symbol)
    
    print(f"Investment Return: ${investment_return:.2f}, Profit or Loss: {profit_or_loss}")


# Running the tests
if __name__ == "__main__":
    print("Testing process_investment function...")
    test_process_investment()

    print("\nTesting get_gemini_stock_recommendations function...")
    test_get_gemini_stock_recommendations()

    print("\nTesting calculate_investment_return function...")
    test_calculate_investment_return()

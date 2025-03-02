from stocks import get_real_time_stock_price, get_historical_percentage_change

# Test real-time stock price fetching
symbol = "AAPL"
real_time_price = get_real_time_stock_price(symbol)
print(f"Real-time stock price of {symbol}: {real_time_price}")

# Test 30-day historical percentage change
percentage_change = get_historical_percentage_change(symbol)
print(f"Percentage change over 30 days for {symbol}: {percentage_change}%")

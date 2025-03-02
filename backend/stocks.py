import yfinance as yf
import os

def get_real_time_stock_price(symbol, interval="5m"):
    """Fetch the latest available stock price using yfinance."""
    try:
        # Fetch stock data using yfinance for real-time price
        data = yf.download(symbol, period="1d", interval=interval)
        if not data.empty:
            latest_price = data['Close'].iloc[-1]  # Get the most recent closing price
            return latest_price
        else:
            print(f"Error fetching real-time price: No data available for {symbol}")
            return None
    except Exception as e:
        print(f"Error fetching real-time price: {e}")
        return None

def get_historical_percentage_change(symbol):
    """Fetch the percentage change in stock price over the last 30 days using yfinance."""
    try:
        # Fetch historical data using yfinance
        data = yf.download(symbol, period="1mo", interval="1d")
        if not data.empty:
            latest_close = data['Close'].iloc[0]  # The first date's close price
            past_close = data['Close'].iloc[-1]  # The last date's close price
            print(f"Latest close: {latest_close}, Past close: {past_close}")
            percentage_change = -1 * ((latest_close - past_close) / past_close) * 100
            return round(percentage_change, 2)
        else:
            print(f"Error fetching historical data: No data available for {symbol}")
            return None
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

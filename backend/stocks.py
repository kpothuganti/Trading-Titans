import requests
import os
#from game_logic import get_gemini_stock_recommendations  # Import the Gemini function

# Store API Key securely
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

def get_real_time_stock_price(symbol, interval="5min"):
    """Fetch the latest available stock price."""
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if f"Time Series ({interval})" in data:
        timestamps = list(data[f"Time Series ({interval})"].keys())
        latest_timestamp = timestamps[0]  # Most recent data point
        latest_price = float(data[f"Time Series ({interval})"][latest_timestamp]["4. close"])
        return latest_price
    else:
        print(f"Error fetching real-time price: {data.get('Note', 'Unknown error')}")
        return None

def get_historical_percentage_change(symbol):
    """Fetch the percentage change in stock price over the last 30 days."""
    params = {
        "function": "TIME_SERIES_DAILY",  # Free endpoint
        "symbol": symbol,
        "outputsize": "full",  # To ensure we get the entire data
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Time Series (Daily)" in data:
        dates = list(data["Time Series (Daily)"].keys())

        dates.sort(reverse=True)

        # Get the last 30 dates, which should be the most recent ones
        recent_dates = dates[:30]

        if len(recent_dates) >= 30:
            latest_close = float(data["Time Series (Daily)"][recent_dates[0]]["4. close"])
            past_close = float(data["Time Series (Daily)"][recent_dates[-1]]["4. close"])
            percentage_change = ((latest_close - past_close) / past_close) * 100
            return round(percentage_change, 2)
        else:
            print("Not enough data for a 30-day change.")
            return None
    else:
        print(f"Error fetching historical data: {data.get('Note', 'Unknown error')}")
        return None


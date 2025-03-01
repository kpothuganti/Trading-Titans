import streamlit as st
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Trading Titans", layout="wide")

# --- Title and Balance ---
col1, col2 = st.columns([5, 1])  # Swap the order of columns
with col1:
    st.title("Trading Titans")
    st.metric(label="Current Balance", value="$10,000")  # Replace with actual balance

with col2:
    st.image("new_images/profile_icon.png", width=50)  # Replace with your profile icon
    st.write(f"Level: {5}")  # Replace with actual level

# --- Recommended Stocks Table ---
st.header("Recommended Stocks")
st.table(
    pd.DataFrame(
        {
            "Stock": ["AAPL", "GOOGL", "MSFT", "TSLA"],
            "Price": ["$150", "$120", "$300", "$250"],
            "Recommendation": ["Buy", "Hold", "Buy", "Sell"],
        }
    )
)

# --- Portfolio Table ---
st.header("Portfolio")
st.table(
    pd.DataFrame(
        {
            "Stock": ["AAPL", "MSFT", "AMZN"],
            "Quantity": [10, 5, 3],
            "Value": ["$1500", "$1500", "$3000"],
        }
    )
)

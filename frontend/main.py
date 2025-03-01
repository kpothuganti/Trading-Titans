import streamlit as st 
import random
import time

def main():
    st.set_page_config(page_title="Stock Trading Game", layout="wide")
    
    # Initialize session state for balance and authentication
    if "balance" not in st.session_state:
        st.session_state.balance = 10000  # Initial balance
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False  # Default state
    
    bg_image_url = "https://stock.adobe.com/search?k=%22graphic+background%22&asset_id=655686862"
    
    # Styling for the header
    st.markdown("""
    <style>
    body {{
    background-image: url('{bg_image_url}');
    background-size: cover;
    background-attachment: fixed;
    }}
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        background-color: #222222;
        color: white;
        border-radius: 10px;
    }
    .header-title {
        font-size: 50px;
        font-weight: bold;
        text-align: left;
        color: #4CAF50;
        text-shadow: 2px 2px 10px rgba(0, 255, 0, 0.7);
    }
    .balance-info {
        font-size: 20px;
        font-weight: bold;
        color: #FFFFFF;
        background-color: #2196F3;
        # padding: 10px 20px;
        border-radius: 10px;
        width: 200px;
        height:40px;
    }
    .stocks-table {
        font-size: 18px;
        color: #FFFFFF;
        background-color: #333333;
        padding: 10px;
        border-radius: 10px;
    }
    .login-container {
        display: flex;
        align-items: center;
    }
            

    </style>
    """, unsafe_allow_html=True)

    # Header Section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # with col1:
    #     st.image("gemini.svg", width=100)  # Update with the actual logo URL or path
    
    with col2:
        st.markdown('<div class="header-title">Trading Titans</div>', unsafe_allow_html=True)

    with col3:
        if st.session_state.logged_in:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()
        else:
            if st.button("Login"):
                st.session_state.logged_in = True
                st.rerun()

    # Display balance at the top
    st.markdown(f'<div class="balance-info">💰 Balance: ${st.session_state.balance}</div>', unsafe_allow_html=True)

    # Dummy stock data
    stocks = {
        "Tesla": round(random.uniform(150, 900), 2),
        "Apple": round(random.uniform(100, 200), 2),
        "Google": round(random.uniform(2000, 3000), 2),
        "Amazon": round(random.uniform(3000, 4000), 2),
        "Bitcoin": round(random.uniform(30000, 60000), 2),
        "Microsoft": round(random.uniform(250, 500), 2),
        "Facebook": round(random.uniform(200, 400), 2),
        "Netflix": round(random.uniform(350, 500), 2),
        "Twitter": round(random.uniform(35, 80), 2),
        "NVIDIA": round(random.uniform(500, 800), 2),
    }
    
    # Sort stocks by price (descending)
    sorted_stocks = sorted(stocks.items(), key=lambda x: x[1], reverse=True)

    # Display the top 10 stocks in order
    st.image("gemini.svg", width=100)
    st.subheader("Stocks")
    st.write('<div class="stocks-table"><ul>', unsafe_allow_html=True)
    for stock, price in sorted_stocks[:10]:  # Display top 10
        st.write(f"<li><strong>{stock}:</strong> ${price}</li>", unsafe_allow_html=True)
    st.write('</ul></div>', unsafe_allow_html=True)

    # Trading section
    st.subheader("💸 Buy Stocks")
    stock_choice = st.selectbox("Select a stock to invest in", list(stocks.keys()))
    quantity = st.number_input("Enter quantity of shares", min_value=1, value=1)
    total_price = quantity * stocks[stock_choice]
    
    if st.button("Invest"):
        if total_price > st.session_state.balance:
            st.error("Insufficient funds!")
        else:
            st.session_state.balance -= total_price
            st.success(f"Successfully bought {quantity} shares of {stock_choice} at ${stocks[stock_choice]} each.")
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()

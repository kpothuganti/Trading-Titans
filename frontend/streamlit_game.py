import streamlit as st
import sqlite3
import sys
import os
import time
import base64
import pandas as pd
sys.path.append('backend')
from game_logic import process_investment, get_gemini_stock_recommendations, calculate_investment_return
print(sys.path)
from stocks import get_real_time_stock_price, get_historical_percentage_change

def connect_db():
    return sqlite3.connect("game.db", check_same_thread=False)

def get_base64(image_path):
    """Encodes an image file to base64."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- Function to set background ---
def set_bg(image_path):
    """Applies a background image using Streamlit-compatible CSS."""
    bg_ext = "jpg"  # Change if needed (e.g., "png")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/{bg_ext};base64,{get_base64(image_path)}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_user_transactions(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_symbol, invested_amount, return_amount, profit_loss, return_on_investment FROM TRANSACTIONS WHERE user_id = ?", (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_user_portfolio(user_id):
    """Get portfolio summary grouped by stock symbol"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            stock_symbol, 
            SUM(invested_amount) as total_invested, 
            SUM(return_amount) as total_return,
            SUM(invested_amount) + SUM(return_amount) as total_stats
        FROM TRANSACTIONS 
        WHERE user_id = ? 
        GROUP BY stock_symbol
    """, (user_id,))
    portfolio = cursor.fetchall()
    conn.close()
    return portfolio

def get_most_frequent_profit_loss(user_id, stock_symbol):
    """Get the most frequent profit/loss status (positive or negative) for a stock"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            CASE WHEN return_amount > 0 THEN 'positive' ELSE 'negative' END as status,
            COUNT(*) as count
        FROM TRANSACTIONS 
        WHERE user_id = ? AND stock_symbol = ?
        GROUP BY CASE WHEN profit_loss > 0 THEN 'positive' ELSE 'negative' END
        ORDER BY count DESC
        LIMIT 1
    """, (user_id, stock_symbol))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "neutral"

def main():
    st.set_page_config(page_title="Trading Titans - Stock Adventure Game", layout="wide")
    
    # Custom CSS for the game UI
    st.markdown("""
        <style>
        .title {
            font-size: 60px;
            font-weight: bold;
            text-align: center;
            color: white;
            text-shadow: 2px 2px 10px rgba(0, 255, 255, 0.8);
            margin-bottom: 20px;
        }
        .balance-box {
            background-color: #1e1e1e;
            border: 2px solid #32CD32;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            font-size: 24px;
            color: #32CD32;
            margin: 10px 0;
            box-shadow: 0 0 10px rgba(50, 205, 50, 0.5);
        }
        .level-box {
            background-color: #1e1e1e;
            border: 2px solid #FFD700;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            font-size: 24px;
            color: #FFD700;
            margin: 10px 0;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        }
        .stock-card {
            padding: 15px;
            border: 1px solid #444;
            border-radius: 10px;
            margin-bottom: 15px;
            background-color: #1e1e1e;
            transition: transform 0.2s;
            height: 180px;
            overflow: hidden;
        }
        .stock-card:hover {
            transform: scale(1.02);
            border-color: cyan;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        }
        .stock-symbol {
            font-weight: bold;
            font-size: 20px;
            color: white;
        }
        .stock-priority {
            color: #AAA;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .stock-advice {
            font-size: 14px;
            color: #DDD;
            height: 80px;
            overflow: hidden;
        }
        .section-header {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 20px 0 10px 0;
            border-left: 5px solid cyan;
        }
        .logout-btn {
            position: absolute;
            top: 10px;
            right: 20px;
            z-index: 1000;
        }
        </style>
        """, unsafe_allow_html=True)
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "users" not in st.session_state:
        st.session_state.users = {}  # Dictionary to store user credentials
    
    if not st.session_state.logged_in:
        show_login("bgg.jpeg")
    else:
        show_dashboard("bgg.jpeg")

def show_login(image_path):
    set_bg(image_path)
    
    st.markdown("""
        <style>
        # .login-container {
        #     max-width: 500px;
        #     margin: 0 auto;
        #     padding: 30px;
        #     background-color: green;
        #     border-radius: 10px;
        #     border: 1px solid #444;
        #     box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
        # }
        # </style>
        # """, unsafe_allow_html=True)
    
    st.markdown("<div class='title'>Trading Titans</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        #st.markdown("<h2 style='color: white;'> <b>Login to Your Account</b></h2>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: white; font-weight: bold;'> Log In to Your Account </h2>", unsafe_allow_html=True)
        #st.subheader("Login to Your Account")
        #st.markdown('<p style="color: white; font-size: 20px;">Username:</p>', unsafe_allow_html=True)
        username = st.text_input(":red[Username]", type = "default")
        #st.markdown('<p style="color: white; font-size: 20px;">Password:</p>', unsafe_allow_html=True)
        password = st.text_input(":red[Password]", type="password")
        
        col_login, col_signup = st.columns(2)
        with col_login:
            if st.button("Login", use_container_width=True):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.balance = user[1]
                    st.session_state.level = user[2]
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.markdown("<p style='color: white; background-color: red; padding: 10px; border-radius: 5px;'>❌ Invalid username or password</p>", unsafe_allow_html=True)

                    #st.error("Invalid username or password")
        
        with col_signup:
            if st.button("Create Account", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_dashboard(image_path):
    # Logout button in top right
    set_bg(image_path)
    st.markdown(
        """
        <div class="logout-btn">
            <form id="logout-form" action="">
                <button type="submit" style="background-color: #FF5555; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
                    Logout
                </button>
            </form>
        </div>
        <script>
            document.getElementById("logout-form").addEventListener("submit", function(e) {
                e.preventDefault();
                window.parent.postMessage({type: "streamlit:userLogout"}, "*");
            });
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # Main title
    st.markdown("<h1 style='color: white; font-weight: bold;'>Trading Titans - Stock Adventure Game </h1>", unsafe_allow_html=True)

    #st.markdown("<div class='title'>Trading Titans</div>", unsafe_allow_html=True)
    
    # User stats in a nicer format with 3 columns
    col_name, col_balance, col_level = st.columns(3)
    
    with col_name:
        st.markdown(f"<h2 style='color: white;'>👤 {st.session_state.username}</h2>", unsafe_allow_html=True)
    
    with col_balance:
        st.markdown(
            f"""
            <div class='balance-box'>
                <div style='font-size: 16px; color: white;'>BALANCE</div>
                <div style='font-size: 28px;'>💰 ${st.session_state.balance:.2f}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col_level:
        st.markdown(
            f"""
            <div class='level-box'>
                <div style='font-size: 16px; color: white;'>LEVEL</div>
                <div style='font-size: 28px;'>🏆 {st.session_state.level}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Initialize session state variables if not present
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = get_gemini_stock_recommendations()
    
    if "selected_stock" not in st.session_state:
        st.session_state.selected_stock = None
    
    # Stock recommendations section with better styling
    st.markdown("<div class='section-header'><h2>📈 Gemini AI Stock Recommendations</h2></div>", unsafe_allow_html=True)
    
    # Display stocks in a row with radio buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    col6, col7, col8, col9, col10 = st.columns(5)
    all_cols = [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10]
    
    # Show stock cards in a row
    for i, stock in enumerate(st.session_state.recommendations[:10]):
        with all_cols[i]:
            stock_card = f"""
            <div class='stock-card'>
                <div class='stock-symbol'>{stock['symbol']}</div>
                <div class='stock-priority'>{stock['priority']}% Recommended</div>
                <div class='stock-advice'>{stock['advice']}</div>
            </div>
            """
            st.markdown(stock_card, unsafe_allow_html=True)
            if st.button(f"Select {stock['symbol']}", key=f"btn_{stock['symbol']}"):
                st.session_state.selected_stock = stock
                st.rerun()
    
    # Show selected stock information with better styling
    if st.session_state.selected_stock:
        st.markdown("<div class='section-header'><h2>🔍 Selected Investment</h2></div>", unsafe_allow_html=True)
        
        col_info, col_action = st.columns([2, 1])
        
        with col_info:
            
            st.markdown(f"<h2 style='color: white;'>{st.session_state.selected_stock['symbol']}</h3>", unsafe_allow_html=True)
            st.markdown(f"""
    <p style="color: white; font-weight: bold; font-size: 16px;">
        AI Advice: {st.session_state.selected_stock['advice']}
    </p>
    <p style="color: white; font-weight: bold; font-size: 16px;">
        Recommended Investment: {st.session_state.selected_stock['priority']}%
    </p>
    """, unsafe_allow_html=True)

            #st.write(f"**AI Advice:** {st.session_state.selected_stock['advice']}")
            #st.write(f"**Recommended Investment:** {st.session_state.selected_stock['priority']}%")
            
            # Get current stock price
            try:
                current_price = get_real_time_stock_price(st.session_state.selected_stock['symbol'])
                if current_price is not None:
                    if isinstance(current_price, pd.Series):
                        current_price = current_price.iloc[0]  # Fix for Series ambiguity error
                    st.markdown(f"<h4 style='color: white;'>💰 Current Price: ${float(current_price):.2f}</h4>", unsafe_allow_html=True)
                    #st.write(f"**Current Price:** ${float(current_price):.2f}")
                
                # Historical performance - Fixed the Series error
                hist_change = get_historical_percentage_change(st.session_state.selected_stock['symbol'])
                if hist_change is not None:
                    if isinstance(hist_change, pd.Series):
                        hist_change = hist_change.iloc[0]  # Fix for Series ambiguity error
                    # Color for performance indicator
                    color = "lightgreen" if hist_change > 0 else "red"
                    st.markdown(
    f"<h4 style='color: white; font-weight: bold;'>30-Day Performance: "
    f"<span style='color:{color}; font-weight: bold;'>{hist_change}% {'▲' if hist_change > 0 else '▼'}</span></h4>",
    unsafe_allow_html=True
)

                    #st.markdown(f"**30-Day Performance:** <span style='color:{color};font-weight:bold;'>{hist_change}% {'▲' if hist_change > 0 else '▼'}</span>", unsafe_allow_html=True)
            except Exception as e:
                # Don't show the error, just handle it silently
                st.write("**Stock Details:** Loading market data...")
        
        with col_action:
            st.markdown("<div class='investment-form'>", unsafe_allow_html=True)
            # Investment amount input
            max_investment = int(st.session_state.balance)
            st.markdown("""
                <style>
                    /* Change the label (header) text color to white */
                    .stNumberInput label {
                        color: white;
                    }
                    
                    /* Change the number input text color to black */
                    .stNumberInput input {
                        color: black;
                    }
                </style>
            """, unsafe_allow_html=True)

            amount = st.number_input(
                "Investment Amount ($)", 
                min_value=1, 
                max_value=max_investment if max_investment > 0 else 1,
                step=1,
                value=min(1000, max_investment)
            )
            
            # Process investment button
            if st.button("Invest", use_container_width=True):
                if amount <= 0:
                    st.error("Please enter a valid investment amount!")
                elif amount > st.session_state.balance:
                    st.error("Not enough balance for this investment!")
                else:
                    # Display the spinner with custom text color
                    with st.spinner("Processing your investment..."):
    # Use st.markdown() to display the custom spinner message in white
                        st.markdown(f"<span style='color: white;'>Processing your investment in {st.session_state.selected_stock['symbol']}...</span>", unsafe_allow_html=True)
    
    # Call process_investment directly from game_logic.py
                        result = process_investment(
                        st.session_state.user_id, 
                        st.session_state.selected_stock['symbol'], 
                        amount
                        )

# Display result message in white after spinner ends
                        if "error" in result:
                            st.markdown(f"<span style='color: white;'>{result['error']}</span>", unsafe_allow_html=True)
                        else:
                            st.session_state.balance = result["new_balance"]
                            st.session_state.level = result["level"]
                            st.success(result["message"])
                            st.markdown(f"<span style='color: white;'>{result['message']}</span>", unsafe_allow_html=True)

                            
                            # Show transaction details
                            st.markdown(f"<span style='color: white;'>Investment: ${amount:.2f}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span style='color: white;'>Return: ${result.get('roi', 0):.2f}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span style='color: white;'>New Balance: ${result['new_balance']:.2f}</span>", unsafe_allow_html=True)
                            
                            # Refresh the page after a short delay
                            time.sleep(3)
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Create two columns for investments and portfolio
    st.markdown("<div class='section-header'><h2>📊 Your Trading Performance</h2></div>", unsafe_allow_html=True)
    col_investments, col_portfolio = st.columns(2)
    
    # Show current investments in the left column
    with col_investments:
        st.markdown("<h2 style='color: white; font-weight: bold;'> 💰 Investment History </h2>", unsafe_allow_html=True)
        #st.subheader("💰 Your Current Investments")
        transactions = get_user_transactions(st.session_state.user_id)
        if transactions:
            # Convert to DataFrame for better display
            df = pd.DataFrame(
                transactions, 
                columns=["Stock", "Invested ($)", "Return ($)", "Profit/Loss", "ROI (%)"]
            )
            
            # Display the dataframe with custom formatting
            st.dataframe(df, height=300)
        else:
            st.markdown("<p style='color: white; font-weight: bold;'>No current investments. Start trading to see your portfolio here!</p>", unsafe_allow_html=True)
            #st.info("No current investments. Start trading to see your portfolio here!")
    
    # Show portfolio summary in the right column
    with col_portfolio:
        st.markdown("<h2 style='color: white; font-weight: bold;'> 📊 Your Portfolio </h2>", unsafe_allow_html=True)
        #st.subheader("📊 Your Portfolio Summary")
        portfolio = get_user_portfolio(st.session_state.user_id)
        if portfolio:
            # Convert to DataFrame - removed ROI column as requested
            portfolio_df = pd.DataFrame(
                portfolio,
                columns=["Symbol", "Total Invested ($)", "Total Return ($)", "Total Profit/Loss ($)"]
            )
            
            # Round numerical values
            for col in ["Total Invested ($)", "Total Return ($)", "Total Profit/Loss ($)"]:
                portfolio_df[col] = portfolio_df[col].round(2)
            
            # Add most frequent profit/loss status column
            portfolio_df["Trend"] = portfolio_df["Symbol"].apply(
                lambda symbol: get_most_frequent_profit_loss(st.session_state.user_id, symbol)
            )
            
            # Format the dataframe for display
            def color_profit_loss(val):
                return f'color: {"green" if val > 0 else "red" if val < 0 else "black"}'
            
            # Display the styled dataframe
            st.dataframe(
                portfolio_df.style.applymap(color_profit_loss, subset=["Total Profit/Loss ($)"]),
                height=300
            )
            
            # Show total portfolio value
            total_invested = portfolio_df["Total Invested ($)"].sum()
            total_return = portfolio_df["Total Return ($)"].sum()
            total_profit = portfolio_df["Total Profit/Loss ($)"].sum()
            
            st.markdown("---")
            #st.markdown(f"<div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-top: 10px;'>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 18px; font-weight: bold; color: white;'>Portfolio Summary</div>", unsafe_allow_html=True)

            st.markdown(f"<div style='font-size: 16px; margin: 5px 0; color: white;'>Total Investment Value: "
            f"<span style='color: white; font-weight: bold;'>${total_invested:.2f}</span></div>", 
            unsafe_allow_html=True)

            
            return_color = "green" if total_return > 0 else "red"
            return_icon = "📈" if total_return > 0 else "📉"
            st.markdown(f"<div style='font-size: 16px; margin: 5px 0; color: white;'>Total Return: "
            f"<span style='color: white; font-weight: bold;'>{return_icon} ${total_return:.2f}</span></div>", 
            unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: white; font-weight: bold;'>No portfolio data yet. Make your first investment!</p>", unsafe_allow_html=True)

    
    # Logout button (visual only - functionality is handled by the top right button)
    if st.button("Logout", key="logout_button_bottom"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def authenticate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, balance, level FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def show_signup():
    st.markdown("<div class='title'>Trading Titans - Sign Up</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.subheader("Create Your Trading Account")
        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        col_signup, col_back = st.columns(2)
        with col_signup:
            if st.button("Sign Up", use_container_width=True):
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif not new_username or not new_password:
                    st.error("Username and password cannot be empty!")
                else:
                    try:
                        create_user(new_username, new_password)
                        st.success("Account created successfully! Please login.")
                        st.session_state.show_signup = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating account: {str(e)}")
        
        with col_back:
            if st.button("Back to Login", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def create_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, balance, level, consecutive_wins, consecutive_losses) VALUES (?, ?, 10000, 1, 0, 0)", (username, password))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    
    if st.session_state.show_signup:
        show_signup()
    else:   
        main()
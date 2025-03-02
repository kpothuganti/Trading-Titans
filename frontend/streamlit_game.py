import streamlit as st
import sqlite3
import sys
import os
sys.path.append('backend')
from game_logic import process_investment, get_gemini_stock_recommendations, calculate_investment_return
print(sys.path)
from stocks import get_real_time_stock_price, get_historical_percentage_change



# Step 1: User Login / Registration
def user_login():
    st.title("Welcome to the Trading Titans Game!")
    
    option = st.selectbox("Choose an option", ["Login", "Register"])

    if option == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            conn = sqlite3.connect("game.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                st.success("Logged in successfully!")
                return user[0], user[1], user[2]  # user_id, balance, level
            else:
                st.error("Invalid credentials. Please register.")
                return None, None, None

    elif option == "Register":
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        if st.button("Register"):
            conn = sqlite3.connect("game.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            st.success("Registration successful! Please login.")
            return None, None, None

# Step 2: Display Current Information (Balance, Level, etc.)
def display_user_info(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance, level FROM users WHERE id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()

    if user_info:
        balance, level = user_info
        st.subheader(f"Current Balance: ${balance}")
        st.subheader(f"Current Level: {level}")
        return balance, level
    else:
        st.error("User information not found.")
        return 0, 0

# Step 3: Show Stock Recommendations from Gemini AI
def display_recommended_stocks():
    st.subheader("Top 10 Stock Recommendations")
    recommendations = get_gemini_stock_recommendations()
    stock_symbols = [rec['symbol'] for rec in recommendations]

    selected_stock = st.selectbox("Select a Stock", stock_symbols)
    investment_amount = st.number_input("Enter Investment Amount ($)", min_value=1.0, max_value=10000.0, step=10.0)
    
    if st.button("Invest"):
        # Assuming user_id is fetched from the session or logged-in status
        user_id = 1  # This should be dynamically set based on logged-in user
        result = process_investment(user_id, selected_stock, investment_amount)
        st.write(result)

# Step 4: Display User's Current Investments (Transactions)
def display_current_investments(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT stock_symbol, invested_amount, return_amount, profit_loss, roi
        FROM TRANSACTIONS
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (user_id,))
    transactions = cursor.fetchall()
    conn.close()

    st.subheader("Your Current Investments")
    if transactions:
        for txn in transactions:
            st.write(f"Stock: {txn[0]}, Invested: ${txn[1]}, Return: ${txn[2]}, Profit/Loss: {txn[3]}, ROI: {txn[4]}%")
    else:
        st.write("No investments found yet.")

# Main Function
def main():
    # Step 1: Login or Register
    user_id, balance, level = user_login()

    if user_id is None:
        # If login or registration fails, show an error and stop the process
        st.error("User not found. Please register first.")
    else:
        # Step 2: Show user information
        display_user_info(user_id)

        # Step 3: Show Stock Recommendations and Allow Investment
        display_recommended_stocks()

        # Step 4: Show User's Current Investments
        display_current_investments(user_id)


if __name__ == "__main__":
    main()


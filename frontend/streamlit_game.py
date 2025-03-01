import streamlit as st
import time
import sqlite3

# Database function to get and add users
def get_user(username, password):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(username, password):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Streamlit UI
def main():
    st.set_page_config(page_title="Trading Titans - Stock Adventure", layout="centered")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "users" not in st.session_state:
        st.session_state.users = {}  # This is just for the session, not database

    if not st.session_state.logged_in:
        show_login()
    else:
        show_game()

def show_login():
    st.markdown("""
        <style>
        .title {
            font-size: 50px;
            font-weight: bold;
            text-align: center;
            color: cyan;
            text-shadow: 2px 2px 10px rgba(0, 255, 255, 0.8);
        }
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80vh;
            padding: 20px;
        }
        .login-form {
            padding: 20px;
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 10px;
            width: 100%;
            max-width: 400px;
        }
        .image-container {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            max-width: 100%;
            padding: 20px;
        }
        .image-container img {
            max-width: 400px;
            width: 100%;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>Cyber Quest - Login</div>", unsafe_allow_html=True)

    # Use a container with two columns for the image and login form
    col1, col2 = st.columns([1, 2])

    with col1:
        # Display image for login page (left-aligned)
        st.markdown("<div class='image-container'>", unsafe_allow_html=True)
        st.image("https://cbx-prod.b-cdn.net/COLOURBOX25446334.jpg?width=800&height=800&quality=70", width=400)  # Replace with your image path
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Create login form inside a div with background color and padding
        st.markdown("<div class='login-form'>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = get_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]  # Store user session ID
                st.session_state.balance = user[3]  # User's balance from DB
                st.session_state.level = user[4]  # User's level from DB
                st.rerun()
            else:
                st.error("Password is incorrect. Please recheck or sign up.")

        if st.button("Create an Account"):
            st.session_state.show_signup = True
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

def show_signup():
    st.markdown("<div class='title'>Create an Account</div>", unsafe_allow_html=True)
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if new_username in st.session_state.users:
            st.error("Username already exists. Choose a different one.")
        elif new_password != confirm_password:
            st.error("Passwords do not match!")
        elif new_username and new_password:
            # Store new user in the database
            add_user(new_username, new_password)
            st.success("Account created successfully! You can now log in.")
            time.sleep(1)
            st.session_state.show_signup = False
            st.rerun()
        else:
            st.error("Please fill in all fields.")
    
    if st.button("Back to Login"):
        st.session_state.show_signup = False
        st.rerun()

def show_game():
    st.markdown("""
        <style>
        .game-title {
            font-size: 60px;
            font-weight: bold;
            text-align: center;
            color: #00FF7F;
            text-shadow: 3px 3px 10px rgba(0, 255, 127, 0.8);
            margin-bottom: 20px;
        }
        .game-description {
            text-align: center;
            font-size: 20px;
            color: #E0FFFF;
            margin-bottom: 30px;
        }
        .game-button {
            display: block;
            margin: 20px auto;
            padding: 15px 30px;
            font-size: 20px;
            background-color: #4682B4;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .game-image {
            display: block;
            margin: 20px auto;
            max-width: 600px;
        }
        body {
            background-color: #121212;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='game-title'>Cyber Quest</div>", unsafe_allow_html=True)
    st.markdown("<p class='game-description'>Prepare for an epic adventure in a cybernetic world!</p>", unsafe_allow_html=True)

    st.image("https://upload.wikimedia.org/wikipedia/commons/0/02/Stock-Market-Icons.jpg", caption="Cyber Quest World", use_column_width=True, output_format="JPEG", clamp=True, width = 600)  # Replace with your game image path

    if st.button("Start Game", key="start_game", on_click=None, type="primary", use_container_width=False):
        with st.spinner("Game is Loading..."):
            time.sleep(2)
        st.success("Game Started!")

    if st.button("Logout", key="logout", on_click=None, type="secondary", use_container_width=False):
        st.session_state.logged_in = False
        st.rerun()

if __name__ == "__main__":
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

    if st.session_state.show_signup:
        show_signup()
    else:
        main()

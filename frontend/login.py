# import streamlit as st
# import time
# import random
# import main  # Import main.py instead of switching pages

# def main():
#     st.set_page_config(page_title="Cyber Quest", layout="centered")
    
#     if "logged_in" not in st.session_state:
#         st.session_state.logged_in = False
#     if "users" not in st.session_state:
#         st.session_state.users = {}
#     if "balance" not in st.session_state:
#         st.session_state.balance = 10000  # Initial balance for stock trading game
    
#     if not st.session_state.logged_in:
#         show_login()
#     else:
#         st.session_state.current_page = "main"
#         main.main()  # Call main.py directly

# def show_login():
#     st.markdown("""
#         <style>
#         .title {
#             font-size: 50px;
#             font-weight: bold;
#             text-align: center;
#             color: cyan;
#             text-shadow: 2px 2px 10px rgba(0, 255, 255, 0.8);
#         }
#         </style>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<div class='title'>Cyber Quest - Login</div>", unsafe_allow_html=True)
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
    
#     if st.button("Login"):
#         if username in st.session_state.users and st.session_state.users[username] == password:
#             st.session_state.logged_in = True
#             st.rerun()
#         else:
#             st.error("Invalid username or password")
    
#     if st.button("Create an Account"):
#         st.session_state.show_signup = True
#         st.rerun()

# def show_signup():
#     st.markdown("<div class='title'>Create an Account</div>", unsafe_allow_html=True)
#     new_username = st.text_input("New Username")
#     new_password = st.text_input("New Password", type="password")
#     confirm_password = st.text_input("Confirm Password", type="password")
    
#     if st.button("Sign Up"):
#         if new_username in st.session_state.users:
#             st.error("Username already exists. Choose a different one.")
#         elif new_password != confirm_password:
#             st.error("Passwords do not match!")
#         elif new_username and new_password:
#             st.session_state.users[new_username] = new_password
#             st.success("Account created successfully! You can now log in.")
#             time.sleep(1)
#             st.session_state.show_signup = False
#             st.rerun()
#         else:
#             st.error("Please fill in all fields.")
    
# if __name__ == "__main__":
#     if "show_signup" not in st.session_state:
#         st.session_state.show_signup = False
    
#     if st.session_state.show_signup:
#         show_signup()
#     else:
#         main()
import streamlit as st
import time

def main():
    st.set_page_config(page_title="Cyber Quest", layout="centered")
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "users" not in st.session_state:
        st.session_state.users = {}  # Dictionary to store user credentials
    
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
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='title'>Cyber Quest - Login</div>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")
    
    if st.button("Create an Account"):
        st.session_state.show_signup = True
        st.rerun()

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
            st.session_state.users[new_username] = new_password
            st.success("Account created successfully! You can now log in.")
            time.sleep(1)
            st.session_state.show_signup = False
            st.rerun()
        else:
            st.error("Please fill in all fields.")

def show_game():
    st.markdown("<div class='title'>Cyber Quest</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Prepare for an epic adventure in a cybernetic world!</p>", unsafe_allow_html=True)
    
    if st.button("Start Game"):
        with st.spinner("Game is Loading..."):
            time.sleep(2)
        st.success("Game Started!")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
if __name__ == "__main__":
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    
    if st.session_state.show_signup:
        show_signup()
    else:   
        main()

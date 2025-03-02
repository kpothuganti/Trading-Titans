import streamlit as st
import requests
import pandas as pd
import time
import sys
import subprocess
import os
import signal
import atexit
from requests.exceptions import ConnectionError, RequestException

# API endpoint configuration
API_BASE_URL = "http://localhost:5001"  # Remove /api from base URL
flask_process = None

def start_flask_backend():
    """Start the Flask backend server"""
    global flask_process
    try:
        # Kill any existing Flask process
        cleanup_flask_process()
        
        # Get the absolute path to the backend directory
        backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
        
        # Verify backend directory exists
        if not os.path.exists(backend_dir):
            st.error(f"Backend directory not found at: {backend_dir}")
            return False
            
        # Verify app.py exists
        app_path = os.path.join(backend_dir, 'app.py')
        if not os.path.exists(app_path):
            st.error(f"app.py not found at: {app_path}")
            return False
        
        st.info("Starting Flask backend server...")
        
        # Start the Flask server with output redirection
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["FLASK_APP"] = "app.py"
        env["FLASK_ENV"] = "development"
        
        flask_process = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )
        
        # Register cleanup function
        atexit.register(cleanup_flask_process)
        
        # Wait for the server to start and check output
        time.sleep(2)
        
        # Check if process is still running
        if flask_process.poll() is not None:
            # Process has terminated, get error output
            stdout, stderr = flask_process.communicate()
            st.error(f"Flask server failed to start.")
            if stdout:
                st.error(f"Output: {stdout}")
            if stderr:
                st.error(f"Error: {stderr}")
            return False
        
        # Verify the server is responding
        max_retries = 5
        for i in range(max_retries):
            try:
                response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Flask backend server started successfully!")
                    return True
            except requests.exceptions.ConnectionError:
                if i < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    st.error("Failed to connect to Flask server after multiple attempts")
                    stdout, stderr = flask_process.communicate()
                    if stdout:
                        st.error(f"Server output: {stdout}")
                    if stderr:
                        st.error(f"Server error: {stderr}")
                    return False
            except Exception as e:
                st.error(f"Error connecting to server: {str(e)}")
                return False
        
        return False
    except Exception as e:
        st.error(f"Failed to start Flask backend: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return False

def cleanup_flask_process():
    """Cleanup function to terminate Flask process"""
    global flask_process
    try:
        if flask_process:
            # Try graceful shutdown first
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)  # Wait up to 5 seconds
            except subprocess.TimeoutExpired:
                # If process doesn't terminate, force kill it
                flask_process.kill()
                flask_process.wait()
            flask_process = None
    except Exception as e:
        st.error(f"Error cleaning up Flask process: {str(e)}")

def check_api_health():
    """Check if the Flask backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            return True
        return start_flask_backend()
    except:
        return start_flask_backend()

def safe_api_call(method, endpoint, **kwargs):
    """Make API calls with proper error handling"""
    max_retries = 2
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': 'http://localhost:8501'
            }
            if 'headers' in kwargs:
                headers.update(kwargs.pop('headers'))
            
            # Ensure endpoint starts with /api/
            if not endpoint.startswith('api/'):
                endpoint = f'api/{endpoint}'
            
            url = f"{API_BASE_URL}/{endpoint}"
            st.info(f"Connecting to: {url}")  # Show the URL being called
            
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, **kwargs)
            else:
                response = requests.post(url, headers=headers, **kwargs)
            
            # Log response status
            if response.status_code != 200:
                st.warning(f"Server responded with status code: {response.status_code}")
                try:
                    error_detail = response.json().get('error', 'No error details provided')
                    st.error(f"Server error: {error_detail}")
                except:
                    pass
            
            # Handle different status codes
            if response.status_code == 403:
                # Try to restart the backend
                if retry_count < max_retries - 1:
                    st.warning("⚠️ Attempting to restart backend server...")
                    if start_flask_backend():
                        retry_count += 1
                        continue
                st.error("⚠️ Access forbidden. Backend server may need to be restarted manually.")
                return None, 403
            
            response.raise_for_status()
            return response.json() if response.content else None, response.status_code
            
        except ConnectionError as ce:
            if retry_count < max_retries - 1:
                st.warning("⚠️ Connection failed. Attempting to restart backend server...")
                if start_flask_backend():
                    retry_count += 1
                    continue
            st.error(f"⚠️ Cannot connect to {url}. Please make sure the backend is running.")
            st.error(f"Connection error details: {str(ce)}")
            return None, 503
        except RequestException as e:
            st.error(f"⚠️ API Error ({e.__class__.__name__}): {str(e)}")
            if hasattr(e.response, 'text'):
                st.error(f"Response text: {e.response.text}")
            return None, 500
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {str(e)}")
            import traceback
            st.error(f"Error details:\n{traceback.format_exc()}")
            return None, 500
        
        retry_count += 1
    
    return None, 500

def main():
    st.set_page_config(page_title="Trading Titans", layout="centered")
    
    # Check if backend is running
    if not check_api_health():
        st.error("⚠️ Backend server is not running.")
        st.info("Attempting to start the backend server automatically...")
        if not start_flask_backend():
            st.error("❌ Failed to start the backend server automatically.")
            st.info("Please try running the backend server manually:")
            st.code("cd backend && python app.py", language="bash")
            st.info("Then refresh this page.")
            return
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "balance" not in st.session_state:
        st.session_state.balance = None
    if "level" not in st.session_state:
        st.session_state.level = None
    if "username" not in st.session_state:
        st.session_state.username = None
    
    if not st.session_state.logged_in:
        show_login()
    else:
        show_dashboard()

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
    
    st.markdown("<div class='title'>Trading Titans - Login</div>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if not username or not password:
            st.error("Please enter both username and password")
            return
        
        st.info("Attempting to log in...")
        data = {
            "username": username,
            "password": password
        }
        
        response, status_code = safe_api_call(
            'post', 
            'login',  # Removed extra 'api/' since safe_api_call adds it
            json=data
        )
        
        if status_code == 200 and response:
            st.session_state.user = response
            st.session_state.logged_in = True
            st.session_state.user_id = response['user_id']
            st.session_state.balance = response['balance']
            st.session_state.level = response['level']
            st.session_state.username = username
            st.success(f"Welcome back, {username}!")
            st.rerun()
        elif status_code == 401:
            st.error("Invalid username or password")
        elif status_code == 403:
            st.error("Access forbidden. Please check if the backend server is running correctly")
        else:
            st.error("Login failed. Please try again.")
    
    if st.button("Create an Account"):
        st.session_state.show_signup = True
        st.rerun()

def show_dashboard():
    st.markdown("<div class='title'>Trading Titans</div>", unsafe_allow_html=True)
    st.write(f"*Welcome, {st.session_state.username}! Your balance: ${st.session_state.balance:,.2f} | Level: {st.session_state.level}*")
    
    # Get stock recommendations
    if "recommendations" not in st.session_state:
        try:
            st.session_state.recommendations = get_gemini_stock_recommendations()
        except Exception as e:
            st.error("⚠️ Failed to get stock recommendations. Please try again later.")
            st.session_state.recommendations = []
    
    if st.session_state.recommendations:
        st.subheader("📈 Gemini AI Stock Recommendations")
        
        # Create a selection widget for stocks
        stock_options = [f"{stock['symbol']} - {stock['advice']}" for stock in st.session_state.recommendations]
        selected_stock_option = st.selectbox("Select a stock to invest in:", stock_options)
        
        # Get the selected stock details
        if selected_stock_option:
            selected_index = stock_options.index(selected_stock_option)
            selected_stock_info = st.session_state.recommendations[selected_index]
            
            st.subheader(f"Investment in {selected_stock_info['symbol']}")
            st.write(f"Advice: {selected_stock_info['advice']}")
            st.write(f"Recommended Investment: {selected_stock_info['priority']}%")
            
            # Investment amount input
            max_investment = int(st.session_state.balance)
            amount = st.number_input(
                "Investment Amount ($)", 
                min_value=1, 
                max_value=max_investment if max_investment > 0 else 1,
                step=1,
                value=min(1000, max_investment)
            )
            
            # Process investment button
            if st.button("Trade & Go Ahead"):
                if amount <= 0:
                    st.error("Please enter a valid investment amount!")
                elif amount > st.session_state.balance:
                    st.error("Not enough balance for this investment!")
                else:
                    with st.spinner(f"Processing your investment in {selected_stock_info['symbol']}..."):
                        response_data, status_code = safe_api_call('post', 'trade', 
                            json={
                                "user_id": st.session_state.user_id,
                                "stock_symbol": selected_stock_info['symbol'],
                                "invested_amount": amount
                            })
                        
                        if status_code == 200 and response_data:
                            # Update session state with new balance and level
                            st.session_state.balance = response_data["new_balance"]
                            st.session_state.level = response_data["level"]
                            
                            # Show success message
                            st.success(response_data["message"])
                            
                            # Show transaction details
                            st.write(f"Investment: ${amount:,.2f}")
                            st.write(f"Return: ${response_data.get('roi', 0):,.2f}")
                            st.write(f"New Balance: ${response_data['new_balance']:,.2f}")
                            
                            # Refresh the page after 2 seconds
                            time.sleep(2)
                            st.rerun()
    
    # Show current investments
    st.subheader("💰 Your Recent Investments")
    response_data, status_code = safe_api_call('get', f'transactions/{st.session_state.user_id}')
    
    if status_code == 200 and response_data:
        if response_data:
            # Convert to DataFrame for better display
            df = pd.DataFrame([
                {
                    "Stock": t["stock_symbol"],
                    "Invested ($)": f"${t['invested_amount']:,.2f}",
                    "Return ($)": f"${t['return_amount']:,.2f}",
                    "Profit/Loss": t["profit_loss"].upper(),
                    "ROI (%)": f"{t['return_on_investment']:,.2f}"
                }
                for t in response_data
            ])
            
            # Apply color formatting
            def color_profit_loss(val):
                color = "green" if val == "PROFIT" else "red"
                return f'color: {color}'
            
            def color_roi(val):
                try:
                    num_val = float(val.replace('%', ''))
                    color = "green" if num_val > 0 else "red"
                    return f'color: {color}'
                except:
                    return 'color: black'
            
            # Display styled dataframe
            st.dataframe(df.style.applymap(color_profit_loss, subset=["Profit/Loss"])
                          .applymap(color_roi, subset=["ROI (%)"]))
        else:
            st.info("No current investments. Start trading to see your portfolio here!")
    
    # Logout button
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def show_signup():
    st.markdown("<div class='title'>Trading Titans - Sign Up</div>", unsafe_allow_html=True)
    new_username = st.text_input("Choose Username")
    new_password = st.text_input("Choose Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Sign Up"):
        if new_password != confirm_password:
            st.error("Passwords do not match!")
        elif not new_username or not new_password:
            st.error("Username and password cannot be empty!")
        else:
            response_data, status_code = safe_api_call('post', 'register', 
                json={"username": new_username, "password": new_password})
            
            if status_code == 201:
                st.success("Account created successfully! Please login.")
                st.session_state.show_signup = False
                st.rerun()
            elif status_code == 409:
                st.error("Username already exists. Please choose another.")
            else:
                st.error("Error creating account. Please try again.")
    
    if st.button("Back to Login"):
        st.session_state.show_signup = False
        st.rerun()

def get_gemini_stock_recommendations():
    # This would ideally be an API endpoint in the Flask backend
    # For now, we'll use the existing function
    try:
        sys.path.append('backend')
        from game_logic import get_gemini_stock_recommendations as get_recommendations
        return get_recommendations()
    except Exception as e:
        st.error(f"⚠️ Failed to get stock recommendations: {str(e)}")
        return []

if __name__ == "__main__":
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    
    if st.session_state.show_signup:
        show_signup()
    else:
        main()


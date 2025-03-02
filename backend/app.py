from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from dotenv import load_dotenv
import os
import sqlite3
import google.generativeai as genai
from game_logic import process_investment

# Load environment variables
load_dotenv()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key='AIzaSyAbTIQ6-4xP68aIVAuty4bFml863XQzCNU')

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "supersecret")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data['username'], hashed_password))
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (data['username'],))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.check_password_hash(user[1], data['password']):
        access_token = create_access_token(identity=user[0], expires_delta=timedelta(hours=1))
        return jsonify(access_token=access_token)
    return jsonify({"message": "Invalid credentials"}), 401

# Make an Investment
@app.route('/invest', methods=['POST'])
@jwt_required()
def invest():
    user_id = get_jwt_identity()
    data = request.json
    result = process_investment(user_id, data['stock_symbol'], data['amount'])
    return jsonify(result)

# Get Stock Recommendations from Gemini AI
@app.route('/recommendations', methods=['GET'])
@jwt_required()
def recommend_stocks():
    prompt = """
    You are an AI stock advisor in a stock market simulation game.
    Provide 5 trending stock recommendations with a brief investment strategy.
    Format:
    SYMBOL - Advice - Suggested Percentage to Invest
    """
    
    response = genai.GenerativeModel('gemini-1.5-pro').generate_content(prompt)
    recommendations = response.text.strip().split("\n")[:5]
    formatted_recommendations = []
    
    for stock in recommendations:
        parts = stock.split(" - ")
        if len(parts) == 3:
            symbol, advice, percentage = parts
            formatted_recommendations.append({
                "symbol": symbol.strip(),
                "advice": advice.strip(),
                "priority": percentage.strip()
            })
    
    return jsonify({"recommendations": formatted_recommendations})

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Stock Market Game API!"})


if __name__ == '__main__':
    app.run(debug=True)

    

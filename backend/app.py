from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from database import init_db
from game_logic import GameLogic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
init_db()

# Initialize game logic
game_logic = GameLogic()

def get_db_connection():
    conn = sqlite3.connect('game.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                      (username, password))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                         (username, password)).fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'user_id': user['id'],
            'username': user['username'],
            'balance': user['balance'],
            'level': user['level']
        })
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/user/<int:user_id>/balance', methods=['GET'])
def get_balance(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user = cursor.execute('SELECT balance FROM users WHERE id = ?',
                         (user_id,)).fetchone()
    conn.close()
    
    if user:
        return jsonify({'balance': user['balance']})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/trade', methods=['POST'])
def make_trade():
    data = request.get_json()
    user_id = data.get('user_id')
    stock_symbol = data.get('stock_symbol')
    invested_amount = data.get('invested_amount')
    
    if not all([user_id, stock_symbol, invested_amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Use game logic to process trade
        result = game_logic.process_trade(user_id, stock_symbol, invested_amount)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    transactions = cursor.execute('''
        SELECT * FROM transactions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC''', (user_id,)).fetchall()
    
    conn.close()
    
    return jsonify([dict(tx) for tx in transactions])

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

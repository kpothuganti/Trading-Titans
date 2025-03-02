from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from database import init_db
from game_logic import process_investment
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow all origins during development
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8501"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Initialize database
init_db()

def get_db_connection():
    """Get database connection with proper path"""
    db_path = os.path.join(os.path.dirname(__file__), 'game.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password, balance, level) VALUES (?, ?, 10000, 1)',
                          (username, password))
            conn.commit()
            
            # Get the newly created user's information
            user = cursor.execute('SELECT id, username, balance, level FROM users WHERE username = ? AND password = ?',
                               (username, password)).fetchone()
            
            if user:
                return jsonify({
                    'message': 'User registered successfully',
                    'user_id': user['id'],
                    'username': user['username'],
                    'balance': user['balance'],
                    'level': user['level']
                }), 201
            return jsonify({'error': 'Failed to create user'}), 500
            
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 409
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user = cursor.execute('SELECT id, username, balance, level FROM users WHERE username = ? AND password = ?',
                            (username, password)).fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'user_id': user['id'],
                'username': user['username'],
                'balance': user['balance'],
                'level': user['level']
            }), 200
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/balance', methods=['GET', 'OPTIONS'])
def get_balance(user_id):
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user = cursor.execute('SELECT balance FROM users WHERE id = ?',
                            (user_id,)).fetchone()
        conn.close()
        
        if user:
            return jsonify({'balance': user['balance']})
        return jsonify({'error': 'User not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trade', methods=['POST', 'OPTIONS'])
def make_trade():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = data.get('user_id')
        stock_symbol = data.get('stock_symbol')
        invested_amount = data.get('invested_amount')
        
        if not all([user_id, stock_symbol, invested_amount]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Use process_investment function directly from game_logic
        result = process_investment(user_id, stock_symbol, invested_amount)
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_transactions(user_id):
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        transactions = cursor.execute('''
            SELECT * FROM transactions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC''', (user_id,)).fetchall()
        
        conn.close()
        
        return jsonify([dict(tx) for tx in transactions]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

import sqlite3

def init_db():
  conn = sqlite3.connect('game.db')
  cursor = conn.cursor()
  cursor.execute("""
                 CREATE TABLE IF NOT EXISTS users(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL,
                 balance REAL DEFAULT 10000.0,
                 level INTEGER DEFAULT 1,
                 consecutive_wins INTEGER DEFAULT 0,
                 consecutive_losses INTEGER DEFAULT 0
                 )
                 """)
  cursor.execute("""
                 CREATE TABLE IF NOT EXISTS TRANSACTIONS (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  stock_symbol TEXT,
                  invested_amount REAL,
                  current_value REAL,
                  return_amount REAL,
                  profit_loss REAL,
                  return_on_investment REAL,
                  advice TEXT,
                  priority_percentage REAL,
                  timestamp DATETTIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id)
                  )
                  """)
  conn.commit()
  conn.close()

init_db()
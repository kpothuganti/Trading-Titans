import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect("game.db")
cursor = conn.cursor()

# Query the TRANSACTIONS table
cursor.execute("SELECT * FROM TRANSACTIONS")
transactions = cursor.fetchall()

# Print the results
for txn in transactions:
    print(f"Transaction ID: {txn[0]}")
    print(f"User ID: {txn[1]}")
    print(f"Stock Symbol: {txn[2]}")
    print(f"Invested Amount: ${txn[3]}")
    print(f"Current Value: ${txn[4]}")
    print(f"Return Amount: ${txn[5]}")
    print(f"Profit/Loss: {txn[6]}")
    print(f"Return on Investment (ROI): {txn[7]}%")
    print(f"Advice: {txn[8]}")
    print(f"Priority Percentage: {txn[9]}")
    print(f"Timestamp: {txn[10]}")
    print("=" * 40)

# Close the connection
conn.close()

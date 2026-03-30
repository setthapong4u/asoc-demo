import sqlite3

conn = sqlite3.connect("demo.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
cur.execute("DELETE FROM users")
cur.execute("INSERT INTO users (id, name) VALUES (1, 'alice')")
cur.execute("INSERT INTO users (id, name) VALUES (2, 'bob')")
conn.commit()
conn.close()

print("demo.db initialized")
from flask import Flask, request
import os
import subprocess
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return "ASOC demo app is running"

# Vulnerability 1: command injection
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    output = subprocess.getoutput(f"ping -c 1 {host}")
    return f"<pre>{output}</pre>"

# Vulnerability 2: SQL injection
@app.route("/user")
def user():
    user_id = request.args.get("id", "1")
    conn = sqlite3.connect("demo.db")
    cur = conn.cursor()
    query = f"SELECT id, name FROM users WHERE id = {user_id}"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return {"rows": rows}

# Vulnerability 3: hardcoded secret
API_KEY = "SUPER-SECRET-12345"

@app.route("/env")
def env():
    return {"secret": API_KEY, "path": os.getenv("PATH", "")}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
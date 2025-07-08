from crewai.tools import tool
import sqlite3
import datetime

@tool("Interaction Logger Tool")
def log_to_db(input: str) -> str:
    """Log any agent input/output to SQLite DB for tracking"""
    conn = sqlite3.connect("agent_logs.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        timestamp TEXT,
        message TEXT
    )''')
    c.execute("INSERT INTO logs VALUES (?, ?)", (datetime.datetime.now().isoformat(), input))
    conn.commit()
    conn.close()
    return "Logged to DB"

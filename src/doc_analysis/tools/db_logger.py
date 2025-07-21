from crewai.tools import tool
import sqlite3
import datetime
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

@tool("Interaction Logger Tool")
def log_to_db(input: str) -> str:
    """Log any agent input/output to SQLite DB for tracking"""
    try:
        conn = sqlite3.connect("agent_logs.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL,
            agent_type TEXT,
            session_id TEXT
        )''')
        c.execute("INSERT INTO logs (timestamp, message) VALUES (?, ?)", 
                 (datetime.datetime.now().isoformat(), input))
        conn.commit()
        conn.close()
        logger.info(f"Successfully logged message to database")
        return "Successfully logged to DB"
    except Exception as e:
        logger.error(f"Failed to log to database: {str(e)}")
        return f"Failed to log to DB: {str(e)}"

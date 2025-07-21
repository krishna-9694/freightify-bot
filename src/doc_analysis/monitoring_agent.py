from crewai import Agent
from crewai.tools import tool
import os
import sqlite3

@tool("System Health Monitor")
def check_system_health() -> str:
    """Monitor system health and suggest improvements"""
    issues = []
    
    # Check vector store
    if not os.path.exists("vectorstore_openai"):
        issues.append("Vector store missing")
    
    # Check database
    try:
        conn = sqlite3.connect("agent_logs.db")
        cursor = conn.execute("SELECT COUNT(*) FROM logs")
        log_count = cursor.fetchone()[0]
        conn.close()
        if log_count > 1000:
            issues.append("Log database needs cleanup")
    except:
        issues.append("Database connection failed")
    
    return f"Health check: {len(issues)} issues found: {', '.join(issues)}" if issues else "System healthy"

monitoring_agent = Agent(
    role='System Monitor',
    goal='Proactively monitor system health and suggest improvements',
    backstory="You continuously monitor the system and provide proactive recommendations.",
    tools=[check_system_health],
    verbose=True
)
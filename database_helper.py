import sqlite3
from datetime import datetime
import os

DB_NAME = "beauty_scores.db"

def init_db():
    """Initialize the database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            score REAL NOT NULL,
            duration_seconds INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_NAME}")

def save_result(score, duration=60):
    """Save the assessment result to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO assessments (timestamp, score, duration_seconds)
        VALUES (?, ?, ?)
    ''', (timestamp, score, duration))
    
    conn.commit()
    conn.close()
    print(f"Result saved: Score={score:.2f}%, Time={timestamp}")

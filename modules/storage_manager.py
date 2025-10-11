import sqlite3
from datetime import datetime

DB_NAME = "analysis_history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            ats_score REAL,
            repositories INTEGER,
            followers INTEGER,
            contributions INTEGER,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(username, role, ats_score, repos, followers, contributions):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO history (username, role, ats_score, repositories, followers, contributions, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, role, ats_score, repos, followers, contributions, date))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, ats_score, repositories, followers, contributions, date FROM history WHERE username=?", (username,))
    data = c.fetchall()
    conn.close()
    return data

def get_leaderboard():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT username, 
               AVG(ats_score) as avg_score,
               SUM(contributions) as total_contributions
        FROM history
        GROUP BY username
        ORDER BY avg_score DESC, total_contributions DESC
        LIMIT 10
    """)
    leaderboard = c.fetchall()
    conn.close()
    return leaderboard
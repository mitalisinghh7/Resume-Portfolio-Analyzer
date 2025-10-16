import sqlite3
from datetime import datetime
from typing import List, Tuple, Any

DB_NAME = "analysis_history.db"

def init_db():

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # create table with points column
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            ats_score REAL,
            repositories INTEGER,
            followers INTEGER,
            contributions INTEGER,
            points INTEGER DEFAULT 0,
            date TEXT
        )
    """)
    conn.commit()

    c.execute("PRAGMA table_info('history')")
    cols = [row[1] for row in c.fetchall()]
    if "points" not in cols:
        c.execute("ALTER TABLE history ADD COLUMN points INTEGER DEFAULT 0")
        conn.commit()

    conn.close()

def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0

def _compute_points(ats_score: Any, contributions: Any) -> int:
    try:
        base = int(round(float(ats_score)))
    except Exception:
        base = 0
    contrib = _safe_int(contributions)
    bonus = contrib // 10
    return max(0, base + bonus)

def save_analysis(username: str, role: str, ats_score: float, repos: Any, followers: Any, contributions: Any):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    repos_i = _safe_int(repos)
    followers_i = _safe_int(followers)
    contributions_i = _safe_int(contributions)
    points = _compute_points(ats_score, contributions_i)

    c.execute("""
        INSERT INTO history (username, role, ats_score, repositories, followers, contributions, points, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, role, ats_score, repos_i, followers_i, contributions_i, points, date))

    conn.commit()
    conn.close()

def get_user_history(username: str) -> List[Tuple]:

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT role, ats_score, repositories, followers, contributions, points, date
        FROM history
        WHERE username = ?
        ORDER BY date DESC
    """, (username,))
    data = c.fetchall()
    conn.close()
    return data

def get_leaderboard() -> List[Tuple]:

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT username,
               AVG(ats_score) as avg_score,
               SUM(contributions) as total_contributions,
               SUM(points) as total_points
        FROM history
        GROUP BY username
        ORDER BY avg_score DESC, total_contributions DESC
        LIMIT 10
    """)
    leaderboard = c.fetchall()
    conn.close()
    return leaderboard
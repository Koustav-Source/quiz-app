import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")


def get_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# ── Questions ──────────────────────────────────────────────────────────────

def get_all_questions():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM questions").fetchall()


def get_questions(category=None, difficulty=None, limit=5):
    query = "SELECT * FROM questions WHERE 1=1"
    params = []
    if category and category != "all":
        query += " AND category = ?"
        params.append(category)
    if difficulty and difficulty != "all":
        query += " AND difficulty = ?"
        params.append(difficulty)
    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_categories():
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT category FROM questions").fetchall()
        return [r["category"] for r in rows]


# ── Users ──────────────────────────────────────────────────────────────────

def create_user(username, email, password_hash, salt):
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, email, password_hash, salt) VALUES (?,?,?,?)",
                (username, email, password_hash, salt),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_user_by_username(username):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def get_user_by_id(user_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()


# ── Quiz Sessions ──────────────────────────────────────────────────────────

def create_session(session_id, user_id, question_ids, category, difficulty, time_limit):
    ids_str = ",".join(str(i) for i in question_ids)
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO quiz_sessions
               (id, user_id, question_ids, category, difficulty, time_limit_secs)
               VALUES (?,?,?,?,?,?)""",
            (session_id, user_id, ids_str, category, difficulty, time_limit),
        )
        conn.commit()


def get_session(session_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM quiz_sessions WHERE id = ?", (session_id,)
        ).fetchone()


def close_session(session_id, score):
    with get_connection() as conn:
        conn.execute(
            "UPDATE quiz_sessions SET submitted_at=CURRENT_TIMESTAMP, score=? WHERE id=?",
            (score, session_id),
        )
        conn.commit()


# ── Leaderboard ────────────────────────────────────────────────────────────

def save_leaderboard_entry(user_id, username, score, total, category, difficulty, time_taken):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO leaderboard
               (user_id, username, score, total, category, difficulty, time_taken_secs)
               VALUES (?,?,?,?,?,?,?)""",
            (user_id, username, score, total, category, difficulty, time_taken),
        )
        conn.commit()


def get_leaderboard(category=None, difficulty=None, limit=20):
    query = """
        SELECT username, score, total,
               ROUND(score * 100.0 / total, 1) AS pct,
               category, difficulty, time_taken_secs, played_at
        FROM leaderboard
        WHERE 1=1
    """
    params = []
    if category and category != "all":
        query += " AND category = ?"
        params.append(category)
    if difficulty and difficulty != "all":
        query += " AND difficulty = ?"
        params.append(difficulty)
    query += " ORDER BY pct DESC, time_taken_secs ASC LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
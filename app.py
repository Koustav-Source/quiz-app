import os
import uuid
import json
import hmac
import hashlib
import base64
import time
import random
from functools import wraps

from flask import (
    Flask, render_template, request, session,
    redirect, url_for, jsonify, flash
)
import database_setup  # runs on import to init DB
import models

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-please")

# ── Auth helpers (no external deps) ───────────────────────────────────────

def _make_salt() -> str:
    return base64.b64encode(os.urandom(16)).decode()


def _hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
    return base64.b64encode(dk).decode()


def _make_token(user_id: int, username: str) -> str:
    payload = json.dumps({"uid": user_id, "un": username, "exp": int(time.time()) + 86400 * 7})
    b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    sig = hmac.new(app.secret_key.encode(), b64.encode(), hashlib.sha256).hexdigest()
    return f"{b64}.{sig}"


def _verify_token(token: str):
    try:
        b64, sig = token.rsplit(".", 1)
        expected = hmac.new(app.secret_key.encode(), b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        data = json.loads(base64.urlsafe_b64decode(b64 + "=="))
        if data["exp"] < int(time.time()):
            return None
        return data
    except Exception:
        return None


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = session.get("token")
        if not token:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        data = _verify_token(token)
        if not data:
            session.clear()
            flash("Session expired. Please log in again.", "warning")
            return redirect(url_for("login"))
        request.current_user = data
        return f(*args, **kwargs)
    return wrapper


def current_user():
    token = session.get("token")
    if not token:
        return None
    return _verify_token(token)


# ── Constants ──────────────────────────────────────────────────────────────

DIFFICULTY_TIME = {"easy": 120, "medium": 150, "hard": 200, "all": 180}
DIFFICULTY_GRACE = 10  # extra seconds allowed for network latency


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    user = current_user()
    categories = models.get_categories()
    return render_template("index.html", user=user, categories=categories)


# ── Auth ────────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")
        salt = _make_salt()
        pw_hash = _hash_password(password, salt)
        ok = models.create_user(username, email, pw_hash, salt)
        if not ok:
            flash("Username or email already taken.", "error")
            return render_template("register.html")
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = models.get_user_by_username(username)
        if not user:
            flash("Invalid username or password.", "error")
            return render_template("login.html")
        pw_hash = _hash_password(password, user["salt"])
        if not hmac.compare_digest(pw_hash, user["password_hash"]):
            flash("Invalid username or password.", "error")
            return render_template("login.html")
        session["token"] = _make_token(user["id"], user["username"])
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ── Quiz ─────────────────────────────────────────────────────────────────────

@app.route("/quiz", methods=["GET"])
@login_required
def quiz_start():
    category   = request.args.get("category", "all")
    difficulty = request.args.get("difficulty", "medium")
    count      = min(int(request.args.get("count", 5)), 10)

    questions = models.get_questions(
        category=category if category != "all" else None,
        difficulty=difficulty if difficulty != "all" else None,
        limit=count,
    )

    if len(questions) < count:
        # Not enough filtered questions — use all
        questions = models.get_all_questions()
        questions = random.sample(list(questions), min(count, len(questions)))

    # Convert to plain dicts so session can serialise them
    q_list = [dict(q) for q in questions]

    session_id = str(uuid.uuid4())
    time_limit = DIFFICULTY_TIME.get(difficulty, 150)
    start_ts   = int(time.time())

    models.create_session(
        session_id=session_id,
        user_id=request.current_user["uid"],
        question_ids=[q["id"] for q in q_list],
        category=category,
        difficulty=difficulty,
        time_limit=time_limit,
    )

    # Store session metadata (NOT the answers — answers stay server-side)
    session["quiz"] = {
        "session_id": session_id,
        "category":   category,
        "difficulty":  difficulty,
        "start_ts":   start_ts,
        "time_limit": time_limit,
        "q_ids":      [q["id"] for q in q_list],
    }

    # Strip answers before sending to template
    safe_questions = []
    for q in q_list:
        safe_questions.append({
            "id":       q["id"],
            "question": q["question"],
            "option1":  q["option1"],
            "option2":  q["option2"],
            "option3":  q["option3"],
            "option4":  q["option4"],
            "category": q["category"],
        })

    return render_template(
        "quiz.html",
        questions=safe_questions,
        session_id=session_id,
        time_limit=time_limit,
        category=category,
        difficulty=difficulty,
    )


@app.route("/quiz/submit", methods=["POST"])
@login_required
def quiz_submit():
    quiz_meta = session.get("quiz")
    if not quiz_meta:
        flash("No active quiz found.", "error")
        return redirect(url_for("index"))

    session_id = quiz_meta["session_id"]
    start_ts   = quiz_meta["start_ts"]
    time_limit = quiz_meta["time_limit"]
    q_ids      = quiz_meta["q_ids"]

    # Server-side time validation
    elapsed = int(time.time()) - start_ts
    if elapsed > time_limit + DIFFICULTY_GRACE:
        session.pop("quiz", None)
        flash("Time's up! Your quiz expired.", "warning")
        return redirect(url_for("index"))

    # Fetch real questions (with answers) from DB
    all_q = {q["id"]: q for q in models.get_all_questions()}

    score    = 0
    breakdown = []
    for qid in q_ids:
        q = all_q.get(qid)
        if not q:
            continue
        user_ans = request.form.get(str(qid), "").strip().lower()
        correct  = q["answer"].strip().lower()
        is_right = user_ans == correct
        if is_right:
            score += 1
        breakdown.append({
            "question":    q["question"],
            "user_answer": request.form.get(str(qid), "—"),
            "correct":     q["answer"],
            "is_right":    is_right,
        })

    total = len(q_ids)
    models.close_session(session_id, score)
    models.save_leaderboard_entry(
        user_id=request.current_user["uid"],
        username=request.current_user["un"],
        score=score,
        total=total,
        category=quiz_meta["category"],
        difficulty=quiz_meta["difficulty"],
        time_taken=elapsed,
    )

    session.pop("quiz", None)

    pct = round(score / total * 100) if total else 0
    return render_template(
        "result.html",
        score=score,
        total=total,
        pct=pct,
        elapsed=elapsed,
        breakdown=breakdown,
        category=quiz_meta["category"],
        difficulty=quiz_meta["difficulty"],
    )


# ── Leaderboard ───────────────────────────────────────────────────────────────

@app.route("/leaderboard")
def leaderboard():
    category   = request.args.get("category", "all")
    difficulty = request.args.get("difficulty", "all")
    entries    = models.get_leaderboard(
        category=category if category != "all" else None,
        difficulty=difficulty if difficulty != "all" else None,
    )
    categories = models.get_categories()
    user = current_user()
    return render_template(
        "leaderboard.html",
        entries=entries,
        categories=categories,
        sel_category=category,
        sel_difficulty=difficulty,
        user=user,
    )


# ── JSON API (for AJAX) ───────────────────────────────────────────────────────

@app.route("/api/leaderboard")
def api_leaderboard():
    category   = request.args.get("category")
    difficulty = request.args.get("difficulty")
    data = models.get_leaderboard(category=category, difficulty=difficulty)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=False)
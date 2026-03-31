import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.executescript('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    option1 TEXT NOT NULL,
    option2 TEXT NOT NULL,
    option3 TEXT NOT NULL,
    option4 TEXT NOT NULL,
    answer TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT "general",
    difficulty TEXT NOT NULL DEFAULT "medium"
);

CREATE TABLE IF NOT EXISTS quiz_sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    question_ids TEXT NOT NULL,
    category TEXT,
    difficulty TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,
    score INTEGER,
    time_limit_secs INTEGER DEFAULT 150
);

CREATE TABLE IF NOT EXISTS leaderboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    username TEXT NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    category TEXT,
    difficulty TEXT,
    time_taken_secs INTEGER,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

cursor.execute("SELECT COUNT(*) FROM questions")
if cursor.fetchone()[0] == 0:
    questions = [
        # Science easy
        ("Which planet is closest to the Sun?", "Venus", "Mercury", "Mars", "Earth", "Mercury", "science", "easy"),
        ("Water is made of hydrogen and?", "Nitrogen", "Carbon", "Oxygen", "Helium", "Oxygen", "science", "easy"),
        ("What force pulls objects to Earth?", "Magnetism", "Friction", "Tension", "Gravity", "Gravity", "science", "easy"),
        ("How many legs does an insect have?", "4", "6", "8", "10", "6", "science", "easy"),
        # Science medium
        ("Chemical symbol for gold?", "Gd", "Go", "Au", "Ag", "Au", "science", "medium"),
        ("Powerhouse of the cell?", "Nucleus", "Ribosome", "Mitochondria", "Vacuole", "Mitochondria", "science", "medium"),
        ("Speed of light in vacuum (km/s)?", "150,000", "300,000", "450,000", "600,000", "300,000", "science", "medium"),
        ("Plants absorb which gas from air?", "Oxygen", "Nitrogen", "CO2", "Argon", "CO2", "science", "medium"),
        # Science hard
        ("Particle carrying weak nuclear force?", "Gluon", "Photon", "W/Z boson", "Graviton", "W/Z boson", "science", "hard"),
        ("DNA replication is semi-conservative, meaning?", "One strand kept", "Both strands kept", "Neither kept", "Random", "One strand kept", "science", "hard"),
        # Technology easy
        ("HTML stands for?", "Hyper Trainer Markup Language", "Hyper Text Markup Language", "High Text Machine Language", "None", "Hyper Text Markup Language", "technology", "easy"),
        ("CSS is used for?", "Structure", "Styling", "Database", "Logic", "Styling", "technology", "easy"),
        ("Which is a programming language?", "HTML", "CSS", "Python", "Photoshop", "Python", "technology", "easy"),
        # Technology medium
        ("Which is not a database?", "MySQL", "MongoDB", "Flask", "SQLite", "Flask", "technology", "medium"),
        ("REST API commonly returns which format?", "XML", "CSV", "JSON", "YAML", "JSON", "technology", "medium"),
        ("Git is used for?", "Styling", "Version control", "Databases", "Networking", "Version control", "technology", "medium"),
        ("Which is a JS runtime?", "Django", "Node.js", "Flask", "Rails", "Node.js", "technology", "medium"),
        # Technology hard
        ("O(log n) is called?", "Linear", "Quadratic", "Logarithmic", "Constant", "Logarithmic", "technology", "hard"),
        ("TCP handshake uses how many steps?", "2", "3", "4", "5", "3", "technology", "hard"),
        # Math easy
        ("2 + 2 = ?", "3", "4", "5", "6", "4", "math", "easy"),
        ("5 * 6 = ?", "30", "35", "25", "20", "30", "math", "easy"),
        ("10% of 200 = ?", "2", "20", "200", "0.2", "20", "math", "easy"),
        # Math medium
        ("Square root of 144?", "11", "12", "13", "14", "12", "math", "medium"),
        ("2 to the power of 10?", "512", "1024", "256", "2048", "1024", "math", "medium"),
        ("Solve: 3x = 27. x = ?", "7", "8", "9", "10", "9", "math", "medium"),
        # Math hard
        ("Derivative of sin(x)?", "cos(x)", "-cos(x)", "-sin(x)", "tan(x)", "cos(x)", "math", "hard"),
        ("Euler's number e is approximately?", "2.512", "2.718", "3.141", "1.618", "2.718", "math", "hard"),
        # History easy
        ("Capital of India?", "Mumbai", "Delhi", "Kolkata", "Chennai", "Delhi", "history", "easy"),
        ("First US President?", "Lincoln", "Jefferson", "Washington", "Adams", "Washington", "history", "easy"),
        # History medium
        ("WW2 ended in which year?", "1943", "1944", "1945", "1946", "1945", "history", "medium"),
        ("Which empire built the Colosseum?", "Greek", "Ottoman", "Roman", "Byzantine", "Roman", "history", "medium"),
        # History hard
        ("Treaty of Westphalia ended which war?", "100 Years War", "30 Years War", "7 Years War", "WW1", "30 Years War", "history", "hard"),
        ("First artificial satellite launched by?", "USA", "China", "India", "USSR", "USSR", "history", "hard"),
    ]
    cursor.executemany(
        "INSERT INTO questions (question,option1,option2,option3,option4,answer,category,difficulty) VALUES (?,?,?,?,?,?,?,?)",
        questions
    )

conn.commit()
conn.close()
print("Database ready.")
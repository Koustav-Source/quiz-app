import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ✅ FIX 1: Safe table creation
cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    answer TEXT
)
''')

# ✅ FIX 2: Check if data already exists
cursor.execute("SELECT COUNT(*) FROM questions")
count = cursor.fetchone()[0]

if count == 0:
    questions = [
        (1, "Capital of India?", "Mumbai", "Delhi", "Kolkata", "Chennai", "Delhi"),
        (2, "2 + 2 = ?", "3", "4", "5", "6", "4"),
        (3, "Python is a?", "Snake", "Language", "Game", "OS", "Language"),
        (4, "HTML stands for?", "Hyper Trainer Marking Language", "Hyper Text Markup Language", "High Text Machine Language", "None", "Hyper Text Markup Language"),
        (5, "CSS is used for?", "Structure", "Styling", "Database", "Logic", "Styling"),
        (6, "Which is a programming language?", "HTML", "CSS", "Python", "Photoshop", "Python"),
        (7, "Which company created Python?", "Google", "Microsoft", "Guido van Rossum", "Apple", "Guido van Rossum"),
        (8, "Which is not a database?", "MySQL", "MongoDB", "Flask", "SQLite", "Flask"),
        (9, "Which is frontend?", "Python", "Java", "HTML", "C++", "HTML"),
        (10, "Which is backend?", "CSS", "HTML", "Flask", "Bootstrap", "Flask"),
        (11, "5 * 6 = ?", "30", "35", "25", "20", "30"),
        (12, "Which is an OS?", "Windows", "HTML", "CSS", "Python", "Windows"),
        (13, "Which is used for AI?", "Python", "HTML", "CSS", "C", "Python"),
        (14, "Which is cloud platform?", "AWS", "C", "HTML", "CSS", "AWS"),
        (15, "Which is version control?", "Git", "HTML", "CSS", "Python", "Git"),
        (16, "Which is not a language?", "Python", "Java", "HTML", "CPU", "CPU"),
        (17, "Which is JS framework?", "React", "Python", "C", "Java", "React"),
        (18, "Which is DB language?", "SQL", "HTML", "CSS", "JS", "SQL"),
        (19, "Which is mobile OS?", "Android", "Python", "HTML", "CSS", "Android"),
        (20, "Which is used for styling?", "HTML", "CSS", "Python", "SQL", "CSS")
    ]

    cursor.executemany("INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?, ?)", questions)

conn.commit()
conn.close()

print("Database ready!")
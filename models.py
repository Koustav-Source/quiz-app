import sqlite3

DB_NAME = "database.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def get_questions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    conn.close()
    return questions
def get_questions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions LIMIT 5")
    data = cursor.fetchall()
    conn.close()
    return data
def get_all_questions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    data = cursor.fetchall()
    conn.close()
    return data

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

def get_connection():
    return sqlite3.connect(db_path)
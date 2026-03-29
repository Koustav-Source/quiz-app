from flask import Flask, render_template, request, session
from models import get_all_questions
import random

app = Flask(__name__)
app.secret_key = "quiz_secret_key"  # required for session

import sqlite3

if not os.path.exists("database.db"):
    import database_setup
else:
    # check table exists
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
    table = cursor.fetchone()
    conn.close()

    if not table:
        import database_setup
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():

    if request.method == 'GET':
        all_questions = get_all_questions()

        # Pick 5 random questions
        selected_questions = random.sample(all_questions, 5)

        # Store in session
        session['questions'] = selected_questions

        return render_template('quiz.html', questions=selected_questions)

    else:
        score = 0
        questions = session.get('questions', [])

        for q in questions:
            qid = str(q[0])
            user_ans = request.form.get(qid)

            if user_ans and user_ans.strip().lower() == q[6].strip().lower():
                score += 1

        return render_template('result.html', score=score, total=len(questions))


if __name__ == '__main__':
    app.run(debug=True)
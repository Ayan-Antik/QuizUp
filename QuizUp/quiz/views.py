from django.shortcuts import render
from django.db import connection


def quiz_detail(request, quiz_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM QUIZ WHERE QUIZ_ID = %s', [quiz_id])
        quiz = cursor.fetchone()
        cursor.execute('SELECT NAME FROM TOPIC WHERE TOPIC_ID = (SELECT TOPIC_ID FROM QUIZ WHERE QUIZ_ID = %s)', [quiz_id])
        topic = cursor.fetchone()[0]
        cursor.execute('''SELECT USERNAME FROM USERS WHERE USER_ID = (SELECT MASTER_ID FROM QUIZ
                                                WHERE QUIZ_ID = %s)''', [quiz_id])
        quizmaster = cursor.fetchone()[0]
        cursor.execute('''SELECT COUNT(*) FROM QUIZ_ATTEMPT GROUP BY QUIZ_ID
                       HAVING QUIZ_ID = %s''', [quiz_id])
        row = cursor.fetchone()
        num_of_played = 0 if row is None else row
        return render(request, 'quiz/quizDetail.html', {'quiz': quiz, 'topic': topic, 'quizmaster': quizmaster,
                                                        'num_of_played': num_of_played})


def play_quiz(request, quiz_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM QUIZ WHERE QUIZ_ID = %s', [quiz_id])
        quiz = cursor.fetchone()
        cursor.execute('SELECT * FROM QUESTION WHERE QUIZ_ID = %s', [quiz_id])
        questions = cursor.fetchall()
    return render(request, 'quiz/quiz.html', {'quiz': quiz, 'questions': questions})
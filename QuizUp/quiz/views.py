from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db import connection
from django.urls import reverse


def has_played(quiz_id, player_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT SCORE FROM QUIZ_ATTEMPT WHERE QUIZ_ID = %s AND PLAYER_ID = %s', [quiz_id, player_id])
        return cursor.fetchone()


def quiz_detail(request, quiz_id):
    if 'id' in request.session and request.session['type'] == "Player":
        player_id = request.session.get('id')
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM TOPIC')
            topics = cursor.fetchall()
            cursor.execute('SELECT * FROM QUIZ WHERE QUIZ_ID = %s', [quiz_id])
            quiz = cursor.fetchone()
            cursor.execute('SELECT NAME FROM TOPIC WHERE TOPIC_ID = (SELECT TOPIC_ID FROM QUIZ WHERE QUIZ_ID = %s)',
                           [quiz_id])
            topic = cursor.fetchone()[0]
            cursor.execute('''SELECT USERNAME FROM USERS WHERE USER_ID = (SELECT MASTER_ID FROM QUIZ
                                                    WHERE QUIZ_ID = %s)''', [quiz_id])
            quizmaster = cursor.fetchone()[0]
            cursor.execute('''SELECT COUNT(*) FROM QUIZ_ATTEMPT GROUP BY QUIZ_ID
                           HAVING QUIZ_ID = %s''', [quiz_id])
            row = cursor.fetchone()
            num_of_played = 0 if row is None else row[0]
            row = has_played(quiz_id, player_id)
            score = -1 if row is None else row[0]
            if row is not None:
                # JHAMELA ASE
                cursor.execute('''SELECT * FROM QUESTION LEFT JOIN QUESTION_ATTEMPT USING (QUESTION_ID)
                                WHERE QUIZ_ID = %s AND PLAYER_ID = %s''', [quiz_id, player_id])
                results = cursor.fetchall()
            else:
                results = None
            cursor.execute('''SELECT USERNAME, MAX(SCORE) FROM QUIZ_ATTEMPT JOIN USERS ON (PLAYER_ID = USER_ID)
                           WHERE QUIZ_ID = %s GROUP BY USERNAME''', [quiz_id])
            top_score = cursor.fetchone()
            cursor.execute('SELECT AVG(SCORE) FROM QUIZ_ATTEMPT WHERE QUIZ_ID = %s', [quiz_id])
            row = cursor.fetchone()
            difficulty = '-'
            if row[0] is not None: # can do it in oracle function
                if row[0] >= 20:
                    difficulty = 'Easy'
                elif row[0] >= 15:
                    difficulty = 'Medium'
                if row[0] > 20:
                    difficulty = 'Hard'
            return render(request, 'quiz/quizDetail.html', {'topics': topics, 'quiz': quiz, 'topic': topic,
                                                            'quizmaster': quizmaster, 'num_of_played': num_of_played,
                                                            'score': score, 'top_score': top_score, 'results': results,
                                                            'difficulty': difficulty})
    else:
        return HttpResponseRedirect(reverse('login'))


def play_quiz(request, quiz_id):
    if 'id' in request.session and request.session['type'] == "Player":
        player_id = request.session.get('id')
        if has_played(quiz_id, player_id) is not None:
            return HttpResponseRedirect(reverse('quiz_detail', args=quiz_id))
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM QUIZ WHERE QUIZ_ID = %s', [quiz_id])
            quiz = cursor.fetchone()
            cursor.execute('SELECT * FROM QUESTION WHERE QUIZ_ID = %s', [quiz_id])
            questions = cursor.fetchall()
            cursor.execute('INSERT INTO QUIZ_ATTEMPT VALUES(%s, %s, 0)', [quiz_id, player_id])
        return render(request, 'quiz/quiz.html', {'quiz': quiz, 'questions': questions})
    else:
        return HttpResponseRedirect(reverse('login'))


def update_score(request):
    if 'id' in request.session and request.session['type'] == "Player":
        player_id = request.session.get('id')
        with connection.cursor() as cursor:
            question_id = request.POST.get('question_id')
            quiz_id = request.POST.get('quiz_id')
            score = request.POST.get('score')
            choice = request.POST.get('choice')
            cursor.execute('INSERT INTO QUESTION_ATTEMPT VALUES(%s, %s, %s, %s)',
                           [question_id, player_id, score, choice])
            row = has_played(quiz_id, player_id)
            prev_score = row[0]
            cursor.execute('UPDATE QUIZ_ATTEMPT SET SCORE = %s WHERE QUIZ_ID = %s AND PLAYER_ID = %s',
                           [prev_score + int(score), quiz_id, player_id])
            return HttpResponse('')
    else:
        return HttpResponseRedirect(reverse('login'))

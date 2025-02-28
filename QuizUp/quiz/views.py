from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
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
            difficulty = quiz[4]
            if difficulty is None:
                difficulty = '-'
            cursor.execute('SELECT NAME,TOPIC_ID '
                           'FROM TOPIC '
                           'WHERE TOPIC_ID = (SELECT TOPIC_ID FROM QUIZ WHERE QUIZ_ID = %s)',
                           [quiz_id])
            topic = cursor.fetchone()
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
                query = '''
                    SELECT *
                    FROM (SELECT * FROM QUESTION WHERE QUIZ_ID = %s) Q,
                         (SELECT * FROM QUESTION_ATTEMPT WHERE PLAYER_ID = %s) QA
                    
                    WHERE Q.QUESTION_ID = QA.QUESTION_ID(+)
                '''
                cursor.execute(query, [quiz_id, player_id])
                results = cursor.fetchall()
                print(results)
            else:
                results = None

            query = '''
                SELECT U.USERNAME, QA.SCORE
                FROM USERS U, QUIZ_ATTEMPT QA
                WHERE QUIZ_ID = %s
                AND SCORE = (SELECT MAX(SCORE) FROM QUIZ_ATTEMPT WHERE QUIZ_ID = %s)
                AND U.USER_ID = QA.PLAYER_ID
  
            '''
            cursor.execute(query, [quiz_id, quiz_id])
            top_score = cursor.fetchone()

            cursor.execute('SELECT USERNAME FROM USERS WHERE USER_ID = %s', [player_id])
            row = cursor.fetchone()
            player_name = row[0]

            query = '''
                SELECT QUIZ_ID, NAME
                FROM QUIZ
                WHERE TOPIC_ID = (SELECT TOPIC_ID FROM QUIZ WHERE QUIZ_ID = %s)
                AND QUIZ_ID <> %s
            '''
            cursor.execute(query, [quiz_id, quiz_id])
            other_quiz = cursor.fetchall()
            if len(other_quiz) == 0:
                other_quiz = None
            #print(other_quiz)
            return render(request, 'quiz/quizDetail.html', {'topics': topics, 'quiz': quiz, 'topic': topic,
                                                            'quizmaster': quizmaster, 'num_of_played': num_of_played,
                                                            'score': score, 'top_score': top_score, 'results': results,
                                                            'player_name': player_name, 'other_quiz': other_quiz})
    else:
        return HttpResponseRedirect(reverse('login'))


def play_quiz(request, quiz_id):
    if 'id' in request.session and request.session['type'] == "Player":
        player_id = request.session.get('id')
        if has_played(quiz_id, player_id) is not None:
            return redirect('quiz_detail', quiz_id=quiz_id)
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM QUIZ WHERE QUIZ_ID = %s', [quiz_id])
            quiz = cursor.fetchone()
            cursor.execute('SELECT * FROM QUESTION WHERE QUIZ_ID = %s ORDER BY QUESTION_ID', [quiz_id])
            questions = cursor.fetchall()
            #print(questions)

            #print(questions)
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
            print(score)
            cursor.execute('INSERT INTO QUESTION_ATTEMPT VALUES(%s, %s, %s, %s)',
                           [question_id, player_id, score, choice])
            '''row = has_played(quiz_id, player_id) --------TRIGGER USED HERE-------
            prev_score = row[0]
            cursor.execute('UPDATE QUIZ_ATTEMPT SET SCORE = %s WHERE QUIZ_ID = %s AND PLAYER_ID = %s',
                           [prev_score + int(score), quiz_id, player_id])'''
            cursor.callproc("UPDATE_DIFFICULTY", [quiz_id])  # PROCEDURE CALLED
            return HttpResponse('')
    else:
        return HttpResponseRedirect(reverse('login'))

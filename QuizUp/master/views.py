from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from django.http import JsonResponse
from .forms import QuizForm
from django.forms import formset_factory


def master_profile(request, master_name):
    if 'id' in request.session and request.session['type'] == "Quizmaster":
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM USERS WHERE USERNAME = %s', [master_name])
            master_id = cursor.fetchone()[0]
            cursor.execute('''SELECT NAME,
            (SELECT NAME FROM TOPIC WHERE TOPIC.TOPIC_ID = QUIZ.TOPIC_ID),
            (SELECT COUNT(*) FROM QUIZ_ATTEMPT WHERE QUIZ_ATTEMPT.QUIZ_ID = QUIZ.QUIZ_ID),
            (SELECT AVG(SCORE) FROM QUIZ_ATTEMPT WHERE QUIZ_ATTEMPT.QUIZ_ID = QUIZ.QUIZ_ID)
            FROM QUIZ WHERE MASTER_ID = %s''', [master_id])
            quiz_infos = cursor.fetchall()
            if quiz_infos is None:
                quiz_infos = []
            cursor.execute('''SELECT * FROM USERS U JOIN QUIZMASTER Q ON (U.USER_ID = Q.MASTER_ID)
            WHERE U.USER_ID <> %s''', [request.session['id']])
            masters = cursor.fetchall()
            cursor.execute('SELECT COUNT(DISTINCT TOPIC_ID) FROM QUIZ WHERE MASTER_ID = %s', [master_id])
            topic_count = cursor.fetchone()[0]
            cursor.execute('''WITH COUNT_TABLE AS ( SELECT TOPIC_ID TID, COUNT(*) CNT FROM QUIZ
                            WHERE MASTER_ID = %s GROUP BY TOPIC_ID)
                            SELECT (SELECT NAME FROM TOPIC WHERE TOPIC_ID = TID)
                            FROM COUNT_TABLE WHERE CNT = (SELECT MAX(CNT) FROM COUNT_TABLE)''', [master_id])
            row = cursor.fetchone()
            favourite_topic = 'None' if row is None else row[0]
            return render(request, 'master/masterHome.html', {'curr_name': request.session['username'],
                                                              'master_name': master_name, 'quiz_infos': quiz_infos,
                                                              'masters': masters, 'topic_count': topic_count,
                                                              'favourite_topic': favourite_topic})
    else:
        return HttpResponseRedirect(reverse("login"))


def create_quiz(request):
    if 'id' in request.session and request.session['type'] == "Quizmaster":
        with connection.cursor() as cursor:
            if request.method == 'POST':
                master_id = request.session["id"]
                cursor.execute('SELECT * FROM TOPIC WHERE NAME = %s', [request.POST['topic']])
                topic_id = cursor.fetchone()[0]
                cursor.execute('''INSERT INTO QUIZ(QUIZ_ID, TOPIC_ID, MASTER_ID, NAME)
                               VALUES(QUIZ_SEQ.NEXTVAL, %s, %s, %s)''',
                               [topic_id, master_id, request.POST['title']])
                for i in range(1, 2):
                    c = str(i)
                    answer = request.POST['a' + c]
                    cursor.execute('''INSERT INTO QUESTION(QUESTION_ID, QUIZ_ID, DESCRIPTION, CHOICE_A, CHOICE_B, CHOICE_C, CHOICE_D, ANSWER)
                                                   VALUES(QUESTION_SEQ.NEXTVAL, QUIZ_SEQ.CURRVAL, %s, %s, %s, %s, %s, %s)''',
                                   [request.POST['q' + c], request.POST['o' + c + '1'], request.POST['o' + c + '2'],
                                    request.POST['o' + c + '3'], request.POST['o' + c + '4'],
                                    request.POST['o' + c + answer]])
                return redirect("master_profile", master_name=request.session['username'])
            else:
                cursor.execute('SELECT * FROM TOPIC')
                topics = cursor.fetchall()
                cursor.execute('''SELECT * FROM USERS U JOIN QUIZMASTER Q ON (U.USER_ID = Q.MASTER_ID)
                            WHERE U.USER_ID <> %s''', [request.session['id']])
                masters = cursor.fetchall()
                return render(request, 'master/createQuiz.html',
                              {'curr_name': request.session['username'], 'topics': topics,
                               'masters': masters})
    else:
        return redirect("login")


def show_questions(request):
    if 'id' in request.session and request.session['type'] == "Quizmaster":
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM QUESTION WHERE QUIZ_ID = %s', [request.GET['quiz_id']])
            questions = cursor.fetchall()
            return JsonResponse({'questions': questions})
    else:
        return HttpResponseRedirect(reverse("login"))

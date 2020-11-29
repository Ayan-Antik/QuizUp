from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from django.http import JsonResponse


def master_home(request, master_name):
    if 'id' in request.session and request.session['type'] == "Quizmaster":
        master_id = request.session.get('id')
        with connection.cursor() as cursor:
            username = master_name
            cursor.execute('SELECT * FROM QUIZ WHERE MASTER_ID = %s', [master_id])
            quizzes = cursor.fetchall()
            if quizzes is None:
                quizzes = []
            return render(request, 'master/masterHome.html', {'username': username, 'quizzes': quizzes})
    else:
        return HttpResponseRedirect(reverse("login"))


def create_quiz(request):
    if 'id' in request.session and request.session['type'] == "Quizmaster":
        master_id = request.session.get('id')
        with connection.cursor() as cursor:
            username = master_name
            cursor.execute('SELECT * FROM QUIZ WHERE MASTER_ID = %s', [master_id])
            quizzes = cursor.fetchall()
            if quizzes is None:
                quizzes = []
            return render(request, 'master/masterHome.html', {'username': username, 'quizzes': quizzes})
    else:
        return HttpResponseRedirect(reverse("login"))


def show_questions(request):
    if 'id' in request.session and request.session['type'] == "Quizmaster":
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM QUESTION WHERE QUIZ_ID = %s', [request.GET['quiz_id']])
            questions = cursor.fetchall()
            return JsonResponse({'questions': questions})
    else:
        return HttpResponseRedirect(reverse("login"))

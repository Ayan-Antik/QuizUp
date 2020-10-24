from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connection
from django.forms.formsets import formset_factory
from django.http import JsonResponse


def follow(request):
    with connection.cursor() as cursor:
        topic_id = request.POST.get('topic_id')
        is_follow = request.POST.get('is_follow')
        if is_follow == 'Follow':
            cursor.execute('INSERT INTO TOPIC_FOLLOW VALUES(%s, 1)', [topic_id])
            is_follow = 'Followed'
        else:
            cursor.execute('DELETE FROM TOPIC_FOLLOW WHERE TOPIC_ID = %s AND FOLLOWER_ID = 1', [topic_id])
            is_follow = 'Follow'
        return JsonResponse({'is_follow': is_follow})


def topic_detail(request, topic_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM TOPIC WHERE TOPIC_ID = %s', [topic_id])
        topic = cursor.fetchone()
        cursor.execute('SELECT * FROM TOPIC_FOLLOW WHERE TOPIC_ID = %s AND FOLLOWER_ID = 1', [topic_id])
        if cursor.fetchone() is None:
            is_follow = 'Follow'
        else:
            is_follow = 'Following'
        return render(request, 'topic/topic.html', {'topic': topic, 'is_follow': is_follow})


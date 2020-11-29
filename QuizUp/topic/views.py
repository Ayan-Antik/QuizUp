from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connection
from django.http import JsonResponse


def update_follow(request):
    if 'id' in request.session and request.session['type'] == "Player":
        player_id = request.session.get('id')
        with connection.cursor() as cursor:
            topic_id = request.POST.get('topic_id')
            is_follow = request.POST.get('is_follow')
            if is_follow == 'Follow':
                cursor.execute('INSERT INTO TOPIC_FOLLOW VALUES(%s, %s)', [topic_id, player_id])
                is_follow = 'Following'
            else:
                cursor.execute('DELETE FROM TOPIC_FOLLOW WHERE TOPIC_ID = %s AND FOLLOWER_ID = %s', [topic_id, player_id])
                is_follow = 'Follow'
            return JsonResponse({'is_follow': is_follow})
    else:
        return HttpResponseRedirect(reverse('login'))


def topic_detail(request, topic_id):
    if 'id' in request.session and request.session['type'] == "Player":
        player_id = request.session.get('id')
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM TOPIC')
            topics = cursor.fetchall()
            cursor.execute('SELECT * FROM TOPIC WHERE TOPIC_ID = %s', [topic_id])
            topic = cursor.fetchone()
            cursor.execute('SELECT * FROM TOPIC_FOLLOW WHERE TOPIC_ID = %s AND FOLLOWER_ID = %s', [topic_id, player_id])
            is_follow = 'Follow' if cursor.fetchone() is None else 'Following'
            cursor.execute('SELECT COUNT(*) FROM TOPIC_FOLLOW GROUP BY TOPIC_ID HAVING TOPIC_ID = %s', [topic_id])
            row = cursor.fetchone()
            num_of_followers = 0 if row is None else row[0]
            cursor.execute('SELECT TOPIC_RANK FROM TOPIC_ATTEMPT WHERE TOPIC_ID = %s AND PLAYER_ID = %s', [topic_id, player_id])
            row = cursor.fetchone()
            rank = '-' if row is None else row[0]
            cursor.execute('''SELECT COUNT(*) FROM QUIZ_ATTEMPT QA JOIN QUIZ Q USING (QUIZ_ID)
                                WHERE Q.TOPIC_ID = %s GROUP BY QA.PLAYER_ID HAVING QA.PLAYER_ID = %s''', [topic_id, player_id])
            row = cursor.fetchone()
            quiz_completed = 0 if row is None else row[0]
            cursor.execute('SELECT COUNT(*) FROM QUIZ GROUP BY TOPIC_ID HAVING TOPIC_ID = %s', [topic_id])
            row = cursor.fetchone()
            total_quiz = 0 if row is None else row[0]
            cursor.execute('SELECT * FROM QUIZ WHERE TOPIC_ID = %s', [topic_id])
            quiz_list = cursor.fetchall()
            if quiz_list is None:
                quiz_list = []

            cursor.execute('''SELECT USERNAME FROM USERS WHERE USER_ID = %s''', [player_id])
            player_info = cursor.fetchone()
            return render(request, 'topic/topic.html', {'topics': topics, 'topic': topic, 'is_follow': is_follow,
                                                        'num_of_followers': num_of_followers, 'rank': rank,
                                                        'quiz_completed': quiz_completed, 'total_quiz': total_quiz,
                                                        'quiz_list': quiz_list, 'player_info': player_info})
    else:
        return HttpResponseRedirect(reverse('login'))



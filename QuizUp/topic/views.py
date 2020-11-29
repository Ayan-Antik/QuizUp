from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connection
from django.http import JsonResponse
from feed.views import time_edit

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



            # TOPIC POSTS

            query = '''
                
                SELECT U.USERNAME,U.IMAGE ,P.POST_ID, P.WRITER_ID,P.DESCRIPTION, P.IMAGE, P.TIME,
                    COUNT(DISTINCT L.PLAYER_ID) AS LIKES, COUNT(DISTINCT C.COMMENT_ID) AS COMMENTS
                FROM POST P, USERS U, LIKES L, COMMENTS C
                WHERE P.POST_ID IN (
                    SELECT T.POST_ID
                    FROM TAG T
                    WHERE T.TOPIC_ID = %s
                    )
                AND P.WRITER_ID = U.USER_ID
                AND P.POST_ID = L.POST_ID(+)
                AND P.POST_ID = C.POST_ID(+)
                GROUP BY U.USERNAME,U.IMAGE ,P.POST_ID, P.WRITER_ID,P.DESCRIPTION, P.IMAGE, P.TIME
                ORDER BY P.TIME DESC
            '''
            cursor.execute(query, [topic_id])
            topic_posts = cursor.fetchall()

            # if PLAYER HAS LIKED A POST
            query = '''
                
                SELECT  P.POST_ID
                FROM POST P
                WHERE P.POST_ID IN (
                    SELECT T.POST_ID
                    FROM TAG T
                    WHERE T.TOPIC_ID = %s
                    )
                AND EXISTS
                (
                    SELECT L.PLAYER_ID
                    FROM LIKES L
                    WHERE L.POST_ID = P.POST_ID
                    AND L.PLAYER_ID = %s /*USER IN SESSION*/
                )
            '''
            cursor.execute(query, [topic_id, player_id])
            liked_posts = cursor.fetchall()
            topic_posts = [list(elem) for elem in topic_posts]

            for post in topic_posts:
                # print(post[2])
                post[6] = time_edit(post[6])
                if post[2] in (like[0] for like in liked_posts):
                    # print(post[2])
                    post.append("Liked")
                else:
                    post.append("Like")
            query = '''
                SELECT U.USERNAME, U.IMAGE
                FROM USERS U 
                WHERE U.USER_ID IN (SELECT FOLLOWER_ID FROM TOPIC_FOLLOW WHERE TOPIC_ID = %s)
            '''
            cursor.execute(query, [topic_id])
            follower_info = cursor.fetchall()

            return render(request, 'topic/topic.html', {'topics': topics, 'topic': topic, 'is_follow': is_follow,
                                                        'num_of_followers': num_of_followers, 'rank': rank,
                                                        'quiz_completed': quiz_completed, 'total_quiz': total_quiz,
                                                        'quiz_list': quiz_list, 'player_info': player_info,
                                                        'topic_posts': topic_posts, 'follower_info': follower_info})
    else:
        return HttpResponseRedirect(reverse('login'))



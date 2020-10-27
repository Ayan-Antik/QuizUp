from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connection
from django.http import JsonResponse


# Create your views here.
def my_profile_detail(request):
    print("HELLO HERE IN MY PROFILE DETAIL")
    if request.session['id'] > -1 and request.session['type'] == "Player":
        player_id = request.session['id']
        print(player_id)
        print(request.session['type'])
        with connection.cursor() as cursor:
            query = '''
                SELECT RANK FROM PLAYER WHERE PLAYER_ID = %s
            '''
            cursor.execute(query, [player_id])
            rank = cursor.fetchone()
            print(rank)

            query = '''
                SELECT USERNAME, EMAIL_ID, IMAGE, ROUND((SYSDATE - DATE_OF_BIRTH) / 365, 0) 
                FROM USERS
                WHERE USER_ID = %s
            '''
            cursor.execute(query, [player_id])
            player_info = cursor.fetchone()
            print(player_info)
            query = '''
                SELECT COUNT(QUIZ_ID) 
                FROM QUIZ_ATTEMPT
                WHERE PLAYER_ID = %s
            '''
            cursor.execute(query, [player_id])
            games = cursor.fetchone()

            #print(games[0])

            query = '''
                SELECT COUNT(FOLLOWER_ID)
                FROM PLAYER_FOLLOW
                WHERE FOLLOWEE_ID = %s
            '''
            cursor.execute(query, [player_id])
            followers = cursor.fetchone()

            query = '''
                SELECT COUNT(FOLLOWEE_ID)
                FROM PLAYER_FOLLOW
                WHERE FOLLOWER_ID = %s
            '''
            cursor.execute(query, [player_id])
            followees = cursor.fetchone()

            query = '''
                SELECT T.NAME, NVL(TA.TOPIC_RANK, 1), T.LOGO
                FROM TOPIC_FOLLOW TF, TOPIC_ATTEMPT TA, TOPIC T
                WHERE TF.TOPIC_ID = TA.TOPIC_ID(+)
                AND T.TOPIC_ID = TF.TOPIC_ID
                AND TF.FOLLOWER_ID = %s
            '''
            cursor.execute(query, [player_id])
            followed_topics = cursor.fetchall()

            print(followed_topics)
            if len(followed_topics) == 0:
                followed_topics = [("None", "-")]

            query = '''
                SELECT U.USERNAME, U.IMAGE
                FROM PLAYER_FOLLOW PF, USERS U
                WHERE PF.FOLLOWER_ID = U.USER_ID
                AND PF.FOLLOWEE_ID = %s
            
            '''
            cursor.execute(query, [player_id])
            follower_info = cursor.fetchall()
            if followers[0] == 0:
                follower_info = [("-", "-")]

            query = '''
                SELECT U.USERNAME, U.IMAGE
                FROM PLAYER_FOLLOW PF, USERS U
                WHERE PF.FOLLOWEE_ID = U.USER_ID
                AND PF.FOLLOWER_ID = %s

                        '''
            cursor.execute(query, [player_id])
            followee_info = cursor.fetchall()
            if followees[0] == 0:
                followee_info = [("-", "-")]

            return render(request, 'profiles/self_profile.html', {'rank': rank[0],
                                                                  'player_info': player_info,
                                                                  'games': games[0],
                                                                  'followers': followers[0],
                                                                  'followees': followees[0],
                                                                  'followed_topics': followed_topics,
                                                                  'follower_info': follower_info,
                                                                  'followee_info': followee_info,

                                                                                })

    else:
        return HttpResponse("ELSED")
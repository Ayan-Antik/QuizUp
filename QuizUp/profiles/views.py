from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connection
from django import forms
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse


# Create your views here.
def my_profile_detail(request):
    #print("HELLO HERE IN MY PROFILE DETAIL")
    if request.session['id'] > -1 and request.session['type'] == "Player":

        player_id = request.session['id']
        #print(player_id)
        #print(request.session['type'])

        if request.method == 'POST':
            print("In post")
            if request.FILES['dp_file']:
                print("In dp")
                image = request.FILES["dp_file"]
                fs = FileSystemStorage(location='media/dp/')
                fs.save(image.name, image)
                storeImage(player_id, 'dp/' + image.name)
                return HttpResponseRedirect(reverse('my_profile_detail'))
            else:
                print("error in img upload")
                return render(request, 'profiles/self_profile.html')

        with connection.cursor() as cursor:
            query = '''
                SELECT RANK FROM PLAYER WHERE PLAYER_ID = %s
            '''
            cursor.execute(query, [player_id])
            rank = cursor.fetchone()
            #print(rank)

            query = '''
                SELECT USERNAME, EMAIL_ID, IMAGE, ROUND((SYSDATE - DATE_OF_BIRTH) / 365, 0) 
                FROM USERS
                WHERE USER_ID = %s
            '''
            cursor.execute(query, [player_id])
            player_info = cursor.fetchone()
            #print(player_info)
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

            #print(followed_topics)
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


            query = '''
                SELECT
                    P.DESCRIPTION, P.IMAGE,
                    TO_CHAR(P.TIME, 'HH:MI AM (Mon DD,YYYY)') AS POST_TIME,
                    P.POST_ID,
                    COUNT(DISTINCT L.PLAYER_ID) AS LIKES, COUNT(DISTINCT C.COMMENT_ID) AS COMMENTS
                FROM
                    POST P, LIKES L, COMMENTS C

                WHERE P.WRITER_ID = %s /*PLAYER_ID*/
                /*AND L.PLAYER_ID = 3 REQUEST.SESSION['ID']*/
                    AND P.POST_ID = L.POST_ID(+)
                    AND P.POST_ID = C.POST_ID(+)
                    
                GROUP BY P.POST_ID, P.DESCRIPTION, P.IMAGE, TO_CHAR(P.TIME, 'HH:MI AM (Mon DD,YYYY)')
                ORDER BY POST_TIME DESC
            '''
            cursor.execute(query, [player_id])
            all_posts = cursor.fetchall()
            #print(all_posts)
            #CHECK IF POST HAS BEEN LIKED BY THE USER IN SESSION


            query = '''
                SELECT  P.POST_ID
                FROM POST P
                WHERE P.WRITER_ID = %s /*PLAYER_ID*/
                AND EXISTS
                    (
                        SELECT L.PLAYER_ID
                        FROM LIKES L
                        WHERE L.POST_ID = P.POST_ID
                        AND L.PLAYER_ID = %s /*USER IN SESSION*/
                    )
            
            '''
            cursor.execute(query, [player_id, request.session['id']])
            liked_posts = cursor.fetchall()
            #change list of tuples (all_post) to list of lists
            all_posts_list = [list(elem) for elem in all_posts]


            for post in all_posts_list:
                #print(post[3])
                if post[3] in (like[0] for like in liked_posts):
                    #print(post[3])
                    post.append("Liked")
                else:
                    post.append("Like")

            #print(all_posts)
            #print(all_posts_list)

            return render(request, 'profiles/self_profile.html', {'rank': rank[0],
                                                                  'player_info': player_info,
                                                                  'games': games[0],
                                                                  'followers': followers[0],
                                                                  'followees': followees[0],
                                                                  'followed_topics': followed_topics,
                                                                  'follower_info': follower_info,
                                                                  'followee_info': followee_info,
                                                                  'all_posts_list': all_posts_list,

                                                                                })


    else:
        return HttpResponse("ELSED")


def storeImage(player_id, location):
    with connection.cursor() as cursor:
        query = '''
            UPDATE USERS
            SET IMAGE = %s
            WHERE USER_ID = %s
        '''
        cursor.execute(query, [location, player_id])
        print(player_id, location)


#def update_like(request):
    #if 'id' in request.session and request.session['type'] == "Player":
        #player_id = request.session.get('id')

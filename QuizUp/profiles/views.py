from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from django import forms
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from feed.views import time_edit


# Create your views here.
def my_profile_detail(request, player_name):
    # print("HELLO HERE IN MY PROFILE DETAIL")
    if request.session['id'] > -1 and request.session['type'] == "Player":

        # player_id = request.session['id']
        # print(player_id)
        # print(request.session['type'])

        if request.method == 'POST' and player_name == request.session['username']:
            # print("In post")
            if request.FILES.get('dp_file', False):
                # print("In dp")
                image = request.FILES["dp_file"]
                fs = FileSystemStorage(location='media/dp/')
                fs.save(image.name, image)
                storeImage(request.session['id'], 'dp/' + image.name)
                return redirect('my_profile_detail', player_name=request.session['username'])

            elif request.POST.get('input', False):
                print(request.POST['input'])
                post_id = request.POST['input']
                delete_post(post_id)
                return redirect('my_profile_detail', player_name=request.session['username'])
            else:
                print("error in img upload")
                return render(request, 'profiles/self_profile.html')

        with connection.cursor() as cursor:
            query = '''
                SELECT USER_ID FROM USERS WHERE USERNAME = %s
            '''
            cursor.execute(query, [player_name])
            player_inf = cursor.fetchone()
            player_id = player_inf[0]

            query = '''
                SELECT RANK FROM PLAYER WHERE PLAYER_ID = %s
            '''
            cursor.execute(query, [player_id])
            rank = cursor.fetchone()
            # print(rank)

            query = '''
                SELECT USERNAME, EMAIL_ID, IMAGE, TO_CHAR(DATE_OF_BIRTH, 'Mon DD, YYYY'), FULLNAME
                FROM USERS
                WHERE USER_ID = %s
            '''
            cursor.execute(query, [player_id])
            player_info = cursor.fetchone()
            # print(player_info)
            query = '''
                SELECT COUNT(QUIZ_ID) 
                FROM QUIZ_ATTEMPT
                WHERE PLAYER_ID = %s
            '''
            cursor.execute(query, [player_id])
            games = cursor.fetchone()

            # print(games[0])

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
                SELECT T.NAME, NVL(TA.LEVEL_, 0), T.LOGO, T.TOPIC_ID
                FROM (SELECT TOPIC_ID FROM TOPIC_FOLLOW WHERE FOLLOWER_ID = %s) TF,
                     (SELECT TOPIC_ID, LEVEL_ FROM TOPIC_ATTEMPT WHERE PLAYER_ID = %s) TA, TOPIC T
                WHERE TF.TOPIC_ID = TA.TOPIC_ID(+)
                AND TF.TOPIC_ID = T.TOPIC_ID
            '''
            cursor.execute(query, [player_id, player_id])
            followed_topics = cursor.fetchall()
            print(followed_topics)

            # print(followed_topics)
            if len(followed_topics) == 0:
                followed_topics = [("None", "-")]

            query = '''
                SELECT U.USERNAME, U.IMAGE, U.USER_ID
                FROM PLAYER_FOLLOW PF, USERS U
                WHERE PF.FOLLOWER_ID = U.USER_ID
                AND PF.FOLLOWEE_ID = %s
            
            '''
            cursor.execute(query, [player_id])
            follower_info = cursor.fetchall()
            if followers[0] == 0:
                follower_info = [("-", "-")]

            query = '''
                SELECT U.USERNAME, U.IMAGE, U.USER_ID
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
                    P.TIME AS POST_TIME,
                    P.POST_ID,
                    COUNT(DISTINCT L.PLAYER_ID) AS LIKES, COUNT(DISTINCT C.COMMENT_ID) AS COMMENTS, GET_TAG(P.POST_ID)
                FROM
                    POST P, LIKES L, COMMENTS C

                WHERE P.WRITER_ID = %s /*PLAYER_ID*/
                /*AND L.PLAYER_ID = 3 REQUEST.SESSION['ID']*/
                    AND P.POST_ID = L.POST_ID(+)
                    AND P.POST_ID = C.POST_ID(+)
                    
                GROUP BY P.POST_ID, P.DESCRIPTION, P.IMAGE, P.TIME
                ORDER BY POST_TIME DESC
            '''
            cursor.execute(query, [player_id])
            all_posts = cursor.fetchall()
            # print(all_posts)
            # CHECK IF POST HAS BEEN LIKED BY THE USER IN SESSION

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
            # change list of tuples (all_post) to list of lists
            all_posts_list = [list(elem) for elem in all_posts]

            for post in all_posts_list:
                # print(post[3])
                post[2] = time_edit(post[2])
                if post[6] is not None:
                    post[6] = list(post[6].split(" "))
                    post[6].pop(0)
                if post[3] in (like[0] for like in liked_posts):
                    # print(post[3])
                    post.append("Liked")
                else:
                    post.append("Like")

            # print(all_posts)
            # print(all_posts_list)

            query = '''
                SELECT * 
                FROM PLAYER_FOLLOW
                WHERE FOLLOWER_ID = %s
                AND FOLLOWEE_ID = %s
            '''
            cursor.execute(query, [request.session['id'], player_id])
            is_follow = 'Follow' if cursor.fetchone() is None else 'Following'

            cursor.execute('SELECT * FROM TOPIC')
            topics = cursor.fetchall()

            return render(request, 'profiles/self_profile.html', {'rank': rank[0],
                                                                  'player_info': player_info,
                                                                  'games': games[0],
                                                                  'followers': followers[0],
                                                                  'followees': followees[0],
                                                                  'followed_topics': followed_topics,
                                                                  'follower_info': follower_info,
                                                                  'followee_info': followee_info,
                                                                  'all_posts_list': all_posts_list,
                                                                  'player_in_session': request.session['username'],
                                                                  'player_name': player_name,
                                                                  'player_id': player_id,
                                                                  'is_follow': is_follow,
                                                                  'topics': topics,

                                                                  })


    else:
        print("Elsed")
        return HttpResponseRedirect(reverse("login"))


def storeImage(player_id, location):
    with connection.cursor() as cursor:
        query = '''
            UPDATE USERS
            SET IMAGE = %s
            WHERE USER_ID = %s
        '''
        cursor.execute(query, [location, player_id])
        print(player_id, location)


def update_like(request):
    if 'id' in request.session and request.session['type'] == "Player":
        player_id = request.session.get('id')
        with connection.cursor() as cursor:
            post_id = request.POST.get('post_id')
            is_liked = request.POST.get('is_liked')
            like_count = int(request.POST.get('like_count'))

            if is_liked == "Like":
                # print("In if, Liking the post...")
                query = '''
                    INSERT INTO LIKES VALUES(%s, %s)
                
                '''
                cursor.execute(query, [post_id, player_id])
                is_liked = "Liked"
                like_count = like_count + 1
            else:
                # print("In Else, DisLiking the post...")
                query = '''
                    DELETE FROM LIKES 
                    WHERE POST_ID = %s
                    AND PLAYER_ID = %s
                '''
                cursor.execute(query, [post_id, player_id])
                is_liked = "Like"
                like_count = like_count - 1

            return JsonResponse({'is_liked': is_liked,
                                 'like_count': like_count})

    else:
        return HttpResponseRedirect(reverse('login'))


def update_player_follow(request):
    if 'id' in request.session and request.session['type'] == "Player":
        follower_id = request.session.get('id')
        with connection.cursor() as cursor:
            followee_id = request.POST.get('followee_id')
            is_follow = request.POST.get('is_follow')
            if is_follow == 'Follow':
                cursor.execute('INSERT INTO PLAYER_FOLLOW VALUES(%s, %s)', [followee_id, follower_id])
                is_follow = 'Following'
            else:
                cursor.execute('DELETE FROM PLAYER_FOLLOW WHERE FOLLOWEE_ID = %s AND FOLLOWER_ID = %s',
                               [followee_id, follower_id])
                is_follow = 'Follow'
            return JsonResponse({'is_follow': is_follow})

    else:
        return HttpResponseRedirect(reverse('login'))


def delete_post(post_id):

    with connection.cursor() as cursor:
        query = '''
            DELETE FROM POST WHERE POST_ID = %s
        '''
        cursor.execute(query, [post_id])
        cursor.close()

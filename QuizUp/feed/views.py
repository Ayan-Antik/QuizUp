from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from django import forms
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from . import forms
from django.http import JsonResponse
# Create your views here.


def time_edit(diff):

    diff_time = datetime.now() - diff
    # print(type(diff)) <class 'datetime.datetime'>
    exact_time = diff.strftime("%I:%M %p")
    exact_date = diff.strftime("%b %d")
    # print(diff_time)
    # print(type(diff_time))<class 'datetime.timedelta'>
    year = round(diff_time.days/365)
    month = round(diff_time.days / 30)
    days = int(datetime.now().strftime("%d")) - int(diff.strftime("%d"))
    #print(days)
    hour = round(diff_time.seconds / 3600)
    minute = round(diff_time.seconds / 60)
    time = 'hello'
    '''ap = 'hi'
    if hour > 12 :
        if datetime.now().strftime("%p") == 'PM':
            ap = 'AM'
        else:
            ap = 'PM'

    else:
        ap = datetime.now().strftime("%p")'''

    if year != 0:
        if year == 1:
            time = "one year ago"
        else:
            time = str(year) + " years ago"

    elif month != 0:
        if month == 1:
            time = exact_date + " at " + exact_time#"one month ago"
        else:
            time = exact_date + " at " + exact_time #str(month) + " months ago"
    elif days != 0:
        if days == 1:
            time = "Yesterday at " + exact_time
        else:
            # time = str(days) + " days ago"
            time = exact_date + " at " + exact_time

    elif hour != 0:
        if hour == 1:
            time = exact_time #"an hour ago"
        else:
            time = exact_time #str(hour) + " hours ago"

    elif minute != 0:
        if minute == 1:
            time = "one minute ago"
        else:
            time = str(minute) + " minutes ago"

    else:
        if diff_time.seconds < 10:
            time = "a few seconds ago"
        else:
            time = str(round(diff_time.seconds)) + " seconds ago"

    # print(time)
    return time


def insert_comment(comment, post_id, writer_id):
    with connection.cursor() as cursor:
        query = '''
            SELECT MAX(COMMENT_ID) 
            FROM COMMENTS
        '''

        cursor.execute(query)
        total_comments = cursor.fetchone()
        comment_id = total_comments[0] + 1
        # print(comment_id)

        query = '''
            INSERT INTO COMMENTS VALUES(%s, %s, %s, %s, SYSDATE)
        
        '''
        cursor.execute(query, [comment_id, writer_id, post_id, comment])


def post_detail(request, post_id):
    if request.session['id'] > -1 and request.session['type'] == "Player":

        player_in_session_name = request.session['username']
        player_in_session_id = request.session['id']

        if request.method == 'POST':
            form = forms.CommentForm(request.POST)

            if form.is_valid():
                comment = form.cleaned_data['comment']
                insert_comment(comment, post_id, player_in_session_id)
                # print(comment)

                return HttpResponseRedirect(reverse('post_detail', args = [post_id]))

            else:
                return HttpResponseRedirect(reverse('post_detail', args = [post_id]))

        with connection.cursor() as cursor:
            query = '''
                SELECT U.USERNAME, U.IMAGE, P.DESCRIPTION, P.IMAGE, P.TIME, P.POST_ID, GET_TAG(P.POST_ID)
                FROM POST P, USERS U
                WHERE P.POST_ID = %s
                AND P.WRITER_ID = U.USER_ID
            
            '''

            cursor.execute(query, [post_id])
            post_info = cursor.fetchone()
            post_info = list(post_info)
            post_info[4] = time_edit(post_info[4])

            query = '''
                SELECT  P.POST_ID
                FROM POST P
                WHERE P.POST_ID = %s
                AND EXISTS
                    (
                        SELECT L.PLAYER_ID
                        FROM LIKES L
                        WHERE L.POST_ID = P.POST_ID
                        AND L.PLAYER_ID = %s /*USER IN SESSION*/
                    )
            
            '''
            cursor.execute(query, [post_id, player_in_session_id])
            liked = cursor.fetchone()

            if post_info[6] is not None:
                post_info[6] = list(post_info[6].split(" "))
                post_info[6].pop(0)

            if liked is None:
                post_info.append("Like")
            else:
                post_info.append("Liked")
            # print(post_info)

            query = '''
                SELECT COUNT(DISTINCT L.PLAYER_ID), COUNT(DISTINCT C.COMMENT_ID)
                FROM POST P, LIKES L, COMMENTS C
                WHERE P.POST_ID = %s
                AND P.POST_ID = L.POST_ID(+)
                AND P.POST_ID = C.POST_ID(+)
                GROUP BY P.POST_ID
                            
            '''
            cursor.execute(query, [post_id])
            react_count = cursor.fetchone()

            query = '''
                SELECT U.USERNAME, U.IMAGE, C.DESCRIPTION, C.TIME
                FROM POST P, COMMENTS C, USERS U
                WHERE P.POST_ID = %s
                AND P.POST_ID = C.POST_ID
                AND C.WRITER_ID = U.USER_ID
                ORDER BY C.TIME
            
            '''

            cursor.execute(query, [post_id])
            comments = cursor.fetchall()
            comments = [list(elem) for elem in comments]
            for comment in comments:
                comment[3] = time_edit(comment[3])
            # print(comments)

            query = '''
            
                SELECT IMAGE
                FROM USERS
                WHERE USER_ID = %s
            
            '''
            cursor.execute(query, [player_in_session_id])
            my_dp = cursor.fetchone()

            query = '''
                SELECT U.USERNAME, U.IMAGE
                FROM POST P, LIKES L, USERS U
                WHERE P.POST_ID = %s
                AND P.POST_ID = L.POST_ID
                AND L.PLAYER_ID = U.USER_ID
            
            '''
            cursor.execute(query, [post_id])
            like_list = cursor.fetchall()

            cursor.execute('SELECT * FROM TOPIC')
            topics = cursor.fetchall()

            return render(request, 'post/post.html',  {'post_info': post_info,
                                                       'player_in_session_name': player_in_session_name,
                                                       'player_in_session_id': player_in_session_id,
                                                       'react_count': react_count,
                                                       'comments': comments,
                                                       'my_dp': my_dp[0],
                                                       'like_list': like_list,
                                                       'topics': topics,

                                                      })

    else:
        return redirect('login')


def feed_detail(request):
    if request.session.get('id', False) is False:
        return redirect('login')
    if request.session['id'] > -1 and request.session['type'] == "Player":

        player_in_session_name = request.session['username']
        player_in_session_id = request.session['id']

        if request.method == 'POST':
            print("In Post Form")
            postform = forms.PostForm(request.POST)

            print(request.POST['post'])
            print(postform.errors)
            if postform.is_valid():
                print("Post form is valid")
                text = postform.cleaned_data['post']
                topics = request.POST.getlist('Topics', False)
                img = request.FILES.get('post_img', False)

                print(text, topics, img)
                insert_post(text, topics, img, player_in_session_id)
                return redirect('feed_detail')

            else:
                print("Post form is not valid")
                return redirect('feed_detail')

        with connection.cursor() as cursor:

            query = '''
                SELECT USERNAME, IMAGE, FULLNAME
                FROM USERS
                WHERE USER_ID = %s
            '''

            cursor.execute(query, [player_in_session_id])
            player_info = cursor.fetchone()

            query = '''
                            SELECT COUNT(FOLLOWER_ID)
                            FROM PLAYER_FOLLOW
                            WHERE FOLLOWEE_ID = %s
                        '''
            cursor.execute(query, [player_in_session_id])
            followers = cursor.fetchone()

            query = '''
                            SELECT COUNT(FOLLOWEE_ID)
                            FROM PLAYER_FOLLOW
                            WHERE FOLLOWER_ID = %s
                        '''
            cursor.execute(query, [player_in_session_id])
            followees = cursor.fetchone()

            query = '''
                SELECT T.NAME, T.LOGO, T.TOPIC_ID
                FROM TOPIC T, TOPIC_FOLLOW TF 
                WHERE TF.FOLLOWER_ID = %s 
                AND T.TOPIC_ID = TF.TOPIC_ID
            '''

            cursor.execute(query, [player_in_session_id])
            followed_topics = cursor.fetchall()

            cursor.execute('SELECT * FROM TOPIC')
            topics = cursor.fetchall()

            query = '''
                SELECT U.USERNAME, U.IMAGE, U.USER_ID
                FROM PLAYER_FOLLOW PF, USERS U
                WHERE PF.FOLLOWER_ID = U.USER_ID
                AND PF.FOLLOWEE_ID = %s

            '''
            cursor.execute(query, [player_in_session_id])
            follower_info = cursor.fetchall()
            if followers[0] == 0:
                follower_info = [("-", "-")]

            query = '''
                SELECT U.USERNAME, U.IMAGE, U.USER_ID
                FROM PLAYER_FOLLOW PF, USERS U
                WHERE PF.FOLLOWEE_ID = U.USER_ID
                AND PF.FOLLOWER_ID = %s

                        '''
            cursor.execute(query, [player_in_session_id])
            followee_info = cursor.fetchall()
            if followees[0] == 0:
                followee_info = [("-", "-")]

            query = '''
                SELECT U.USERNAME,U.IMAGE ,P.POST_ID, P.WRITER_ID,P.DESCRIPTION, P.IMAGE, P.TIME,
                    COUNT(DISTINCT L.PLAYER_ID) AS LIKES, COUNT(DISTINCT C.COMMENT_ID) AS COMMENTS, GET_TAG(P.POST_ID)
                FROM POST P, USERS U, LIKES L, COMMENTS C
                WHERE P.WRITER_ID IN (SELECT FOLLOWEE_ID FROM PLAYER_FOLLOW WHERE FOLLOWER_ID = %s)
                AND P.WRITER_ID = U.USER_ID
                AND P.POST_ID = L.POST_ID(+)
                AND P.POST_ID = C.POST_ID(+)
                GROUP BY U.USERNAME,U.IMAGE ,P.POST_ID, P.WRITER_ID,P.DESCRIPTION, P.IMAGE, P.TIME
                UNION
                SELECT U.USERNAME,U.IMAGE ,P.POST_ID, P.WRITER_ID,P.DESCRIPTION, P.IMAGE, P.TIME,
                    COUNT(DISTINCT L.PLAYER_ID) AS LIKES, COUNT(DISTINCT C.COMMENT_ID) AS COMMENTS, GET_TAG(P.POST_ID)
                FROM POST P, USERS U, LIKES L, COMMENTS C
                WHERE P.POST_ID IN (
                    SELECT DISTINCT (T.POST_ID)
                    FROM TAG T
                    WHERE T.TOPIC_ID IN (SELECT TF.TOPIC_ID FROM TOPIC_FOLLOW TF WHERE FOLLOWER_ID = %s)
                    )
                AND P.WRITER_ID = U.USER_ID
                
                AND P.POST_ID = L.POST_ID(+)
                AND P.POST_ID = C.POST_ID(+)
                GROUP BY U.USERNAME,U.IMAGE ,P.POST_ID, P.WRITER_ID,P.DESCRIPTION, P.IMAGE, P.TIME
                UNION
                SELECT U.USERNAME,U.IMAGE ,P.POST_ID, P.WRITER_ID,P.DESCRIPTION, P.IMAGE, P.TIME,
                    COUNT(DISTINCT L.PLAYER_ID) AS LIKES, COUNT(DISTINCT C.COMMENT_ID) AS COMMENTS, GET_TAG(P.POST_ID)
                FROM POST P, USERS U, LIKES L, COMMENTS C
                WHERE P.WRITER_ID = %s
                AND P.WRITER_ID = U.USER_ID
                
                AND P.POST_ID = L.POST_ID(+)
                AND P.POST_ID = C.POST_ID(+)
                GROUP BY U.USERNAME,U.IMAGE ,P.POST_ID, P.WRITER_ID,P.DESCRIPTION, P.IMAGE, P.TIME
                ORDER BY TIME DESC
            
            '''
            cursor.execute(query, [player_in_session_id, player_in_session_id, player_in_session_id])
            all_posts = cursor.fetchall()

            query = '''
                SELECT  P.POST_ID
                FROM POST P
                WHERE P.WRITER_ID IN (SELECT FOLLOWEE_ID FROM PLAYER_FOLLOW WHERE FOLLOWER_ID = %s) /*PLAYER_ID*/
                AND EXISTS
                (
                    SELECT L.PLAYER_ID
                    FROM LIKES L
                    WHERE L.POST_ID = P.POST_ID
                    AND L.PLAYER_ID = %s /*USER IN SESSION*/
                )
                UNION
                SELECT  P.POST_ID
                FROM POST P
                WHERE P.POST_ID IN (
                    SELECT DISTINCT (T.POST_ID)
                    FROM TAG T
                    WHERE T.TOPIC_ID IN (SELECT TF.TOPIC_ID FROM TOPIC_FOLLOW TF WHERE FOLLOWER_ID = %s)
                    )
                AND EXISTS
                (
                    SELECT L.PLAYER_ID
                    FROM LIKES L
                    WHERE L.POST_ID = P.POST_ID
                    AND L.PLAYER_ID = %s /*USER IN SESSION*/
                )
                UNION
                SELECT P.POST_ID
                FROM POST P
                WHERE P.WRITER_ID = %s
                AND EXISTS 
                (
                    SELECT L.PLAYER_ID
                    FROM LIKES L
                    WHERE L.POST_ID = P.POST_ID
                    AND L.PLAYER_ID = %s /*USER IN SESSION*/
                )
            '''

            cursor.execute(query, [player_in_session_id, player_in_session_id, player_in_session_id,
                                   player_in_session_id, player_in_session_id, player_in_session_id])
            liked_posts = cursor.fetchall()

            # change list of tuples (all_post) to list of lists
            all_posts_list = [list(elem) for elem in all_posts]

            for post in all_posts_list:

                post[6] = time_edit(post[6])
                if post[9] is not None:
                    post[9] = list(post[9].split(" "))
                    post[9].pop(0)

                if post[2] in (like[0] for like in liked_posts):
                    # print(post[2])
                    post.append("Liked")
                else:
                    post.append("Like")
               # print(post)
            query = '''
                
                SELECT *
                FROM (  SELECT   U.USERNAME, P.RANK, U.IMAGE
                        FROM PLAYER P, USERS U
                        WHERE P.PLAYER_ID = U.USER_ID
                        ORDER BY P.RANK DESC) LB
                WHERE ROWNUM <=5
            
            '''

            cursor.execute(query)
            leaderboard = cursor.fetchall()



            cursor.close()
            return render(request, 'feed/feed.html', {'player_info': player_info,
                                                      'followers': followers[0],
                                                      'followees': followees[0],
                                                      'follower_info': follower_info,
                                                      'followee_info': followee_info,
                                                      'followed_topics': followed_topics,
                                                      'topics': topics,
                                                      'all_posts_list': all_posts_list,
                                                      'leaderboard': leaderboard,




                                                  })

    else:
        return redirect('login')


def insert_post(text, topics, image, player_id):
    with connection.cursor() as cursor:

        cursor.execute("SELECT MAX(POST_ID) FROM POST")
        row = cursor.fetchone()
        post_id = row[0] + 1

        if image is not False:
            fs = FileSystemStorage(location='media/post/')
            fs.save(image.name, image)

            query = '''
                INSERT INTO POST VALUES(%s, %s, %s, %s, SYSDATE)
            '''
            cursor.execute(query, [post_id, player_id, text, 'post/' + image.name])

        elif image is False:
            query = '''
                            INSERT INTO POST VALUES(%s, %s, %s, NULL, SYSDATE)
                        '''
            cursor.execute(query, [post_id, player_id, text])

        if topics is not False:
            for topic in topics:
                query = '''
                    SELECT TOPIC_ID FROM TOPIC WHERE NAME = %s
                '''
                cursor.execute(query, [topic])
                row = cursor.fetchone()
                topic_id = row[0]
                print(str(topic_id) + ": " + topic)

                query = '''
                    INSERT INTO TAG VALUES (%s, %s)
                '''

                cursor.execute(query, [post_id, topic_id])

    cursor.close()

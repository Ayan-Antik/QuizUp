from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from django import forms
from datetime import datetime
from django.http import JsonResponse
# Create your views here.


def time_edit(diff):
    diff_time = datetime.now() - diff
    # print(diff_time)
    # print(type(diff_time))
    year = round(diff_time.days/365)
    month = round(diff_time.days / 30)
    days = diff_time.days
    hour = round(diff_time.seconds / 3600)
    minute = round(diff_time.seconds / 60)
    time = 'hello'

    if year != 0:
        if year == 1:
            time = "one year ago"
        else:
            time = str(year) + " years ago"

    elif month != 0:
        if month == 1:
            time = "one month ago"
        else:
            time = str(month) + " months ago"
    elif days != 0:
        if days == 1:
            time = "one day ago"
        else:
            time = str(days) + " days ago"

    elif hour != 0:
        if hour == 1:
            time = "one hour ago"
        else:
            time = str(hour) + " hours ago"

    elif minute != 0:
        if minute == 1:
            time = "one minute ago"
        else:
            time = str(minute) + " minutes ago"

    else:
        time = str(round(diff_time.seconds)) + " seconds ago"

    # print(time)
    return time


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)


def insert_comment(comment, post_id, writer_id):
    with connection.cursor() as cursor:
        query = '''
            SELECT COUNT(COMMENT_ID) 
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
            form = CommentForm(request.POST)

            if form.is_valid():
                comment = form.cleaned_data['comment']
                insert_comment(comment, post_id, player_in_session_id)
                # print(comment)

                return HttpResponseRedirect(reverse('post_detail', args = [post_id]))

            else:
                return HttpResponseRedirect(reverse('post_detail', args = [post_id]))

        with connection.cursor() as cursor:
            query = '''
                SELECT U.USERNAME, U.IMAGE, P.DESCRIPTION, P.IMAGE, P.TIME, P.POST_ID
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

            return render(request, 'post/post.html',  {'post_info' : post_info,
                                                       'player_in_session_name': player_in_session_name,
                                                       'player_in_session_id': player_in_session_id,
                                                       'react_count': react_count,
                                                       'comments': comments,
                                                       'my_dp': my_dp[0],
                                                       'like_list': like_list,

                                                      })

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from django import forms
from django.http import JsonResponse
# Create your views here.


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
        #print(comment_id)

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
                #print(comment)

                return HttpResponseRedirect(reverse('post_detail', args = [post_id]))

            else:
                return HttpResponseRedirect(reverse('post_detail', args = [post_id]))

        with connection.cursor() as cursor:
            query = '''
                SELECT U.USERNAME, U.IMAGE, P.DESCRIPTION, P.IMAGE, TO_CHAR(P.TIME, 'HH:MI AM (Mon DD,YYYY)') AS POST_TIME, P.POST_ID
                FROM POST P, USERS U
                WHERE P.POST_ID = %s
                AND P.WRITER_ID = U.USER_ID
            
            '''

            cursor.execute(query, [post_id])
            post_info = cursor.fetchone()


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
            post_info = list(post_info)

            if liked is None:
                post_info.append("Like")
            else:
                post_info.append("Liked")

            #print(post_info)

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
                SELECT U.USERNAME, U.IMAGE, C.DESCRIPTION, TO_CHAR(C.TIME, 'HH:MI AM (Mon DD,YYYY)')
                FROM POST P, COMMENTS C, USERS U
                WHERE P.POST_ID = %s
                AND P.POST_ID = C.POST_ID
                AND C.WRITER_ID = U.USER_ID
                ORDER BY C.TIME
            
            '''

            cursor.execute(query, [post_id])
            comments = cursor.fetchall()
            #print(comments)

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

            return render(request, 'post/post.html', { 'post_info' : post_info,
                                                       'player_in_session_name': player_in_session_name,
                                                       'player_in_session_id': player_in_session_id,
                                                       'react_count': react_count,
                                                       'comments': comments,
                                                       'my_dp': my_dp[0],
                                                       'like_list': like_list,



                                                             })
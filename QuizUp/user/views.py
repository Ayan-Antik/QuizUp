from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connection
from . import forms


def abc(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT count(*) FROM USERS')
        row = cursor.fetchone()


        # print(userdict)
        return HttpResponse("Hi")


def LogIn(request):
    # print("In Login")
    pagehtml = request.path.split('/')[2]
    print(pagehtml)

    if request.method == 'POST':
        # print("method is POST")
        form = forms.LoginForm(request.POST)
        # print(request.POST['username'])
        if form.is_valid():
            # print("FORM IS VALID")
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            id = authenticate(username, password, pagehtml)
            if id >= 0:
                print("Login Successful")

                request.session['id'] = id

                if pagehtml == "login":
                    request.session['type'] = "Player"

                elif pagehtml == "Quizmasterlogin":
                    request.session['type'] = "Quizmaster"

                print("id: " + str(request.session['id']) + " Type of user: " + request.session['type'])
                # TODO: send to homepage/ Question setter page
                return render(request, 'user/signup.html')
            else:
                # authentication error
                return render(request, 'user/' + pagehtml + '.html')
        else:
            print("FORM NOT VALID???")
            return render(request, 'user/' + pagehtml + '.html')

    else:
        print(request.method)
        return render(request, 'user/' + pagehtml + '.html')


def authenticate(username, password, pagehtml):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM USERS WHERE USERNAME = %s', [username])
        user_row = cursor.fetchone()
        #print(user_row)
        user_id = user_row[0]

        if user_row is not None:
            if user_row[2] == password:
                # check if user exists in player or quizmaster table
                # 1 for player
                if pagehtml == "login":

                    cursor.execute('SELECT * FROM PLAYER WHERE PLAYER_ID = %s', [user_id])
                    player_info = cursor.fetchone()

                    if player_info is not None:
                        return player_info[0]
                    else:
                        print("User is not a player")
                        return -1

                elif pagehtml == "Quizmasterlogin":
                    cursor.execute('SELECT * FROM QUIZMASTER WHERE MASTER_ID = %s', [user_id])
                    master_info = cursor.fetchone()

                    if master_info is not None:
                        return master_info[0]
                    else:
                        print("User is not a Quizmaster")
                        return -1
            else:
                print("Password doesn't match")
                return -1

        else:
            print("No such User")
            return -1


def SignUp(request):

    if request.method == 'POST':
        signupform = forms.SignUpForm(request.POST)

        if signupform.is_valid():
            print("Form is val")
            username = signupform.cleaned_data['username']
            dob = signupform.cleaned_data['dob']
            email = signupform.cleaned_data['email']
            password1 = signupform.cleaned_data['password1']
            password2 = signupform.cleaned_data['password2']

            #print(username, dob, email)

            if validUsername(username) and (password1 == password2):
                createPlayer(username, password1, email, dob)
                print("User Created")
                # TODO : send user to home
                return render(request, 'user/login.html')


            else:
                print("Signup Form Not Properly filled")
                return render(request, 'user/signup.html')
        else:
            print("Signup Form Error")
            return render(request, 'user/signup.html')

    else:
        print("Not Post Method")
        return render(request, 'user/signup.html')


def validUsername(username):
    with connection.cursor() as cursor:
        cursor.execute('SELECT USERNAME FROM USERS WHERE USERNAME = %s', [username])
        row = cursor.fetchone()
        if row is None:
            # Username Valid
            return True
        else:
            return False


def createPlayer(username, password, email, dob):
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM USERS')
        row = cursor.fetchone()
        total_users = row[0]
        user_query = '''
            INSERT INTO USERS VALUES (%s , %s, %s, %s, 'signup/default-dp.png', %s)
        
        '''
        player_query = '''
            INSERT INTO PLAYER VALUES (%s, 1)
        '''
        cursor.execute(user_query, [total_users + 1, username, password, email, dob])
        cursor.execute(player_query, [total_users + 1])

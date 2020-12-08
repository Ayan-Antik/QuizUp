import hashlib

from django.db.utils import IntegrityError, DatabaseError
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from . import forms


def clear_session(request):
    try:
        del request.session['id']
        del request.session['type']
        del request.session['username']
    except KeyError:
        pass


def root(request):
    if 'id' in request.session:
        if request.session['type'] == 'Player':
            return redirect('feed_detail')
        else:
            return redirect('master_profile', master_name=request.session['username'])
    else:
        return redirect('login')


def LogIn(request):
    # print("In Login")
    pagehtml = request.path.split('/')[2]
    #print(pagehtml)

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
                # clear all prev log ins
                clear_session(request)

                request.session['id'] = id
                request.session['username'] = username

                if pagehtml == "login":
                    request.session['type'] = "Player"
                    # sending to his own profile
                    #return HttpResponseRedirect(reverse('my_profile_detail', player_id=request.session['id']))
                    return redirect('feed_detail')

                elif pagehtml == "Quizmasterlogin":
                    request.session['type'] = "Quizmaster"
                    return redirect('master_profile', master_name=username)

                #print("id: " + str(request.session['id']) + " Type of user: " + request.session['type'])
                # TODO: send to homepage/ Question setter page

                #return render(request, 'user/signup.html')
            else:
                # authentication error
                return render(request, 'user/' + pagehtml + '.html', {'error': 'Incorrect Username or Password!'})
        else:
            print("FORM NOT VALID???")
            return render(request, 'user/' + pagehtml + '.html')

    else:
        #print(request.method)
        return render(request, 'user/' + pagehtml + '.html')


def authenticate(username, password, pagehtml):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM USERS WHERE USERNAME = %s', [username])
        user_row = cursor.fetchone()
        #print(user_row)

        if user_row is not None:
            user_id = user_row[0]
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            if user_row[2] == hashed_password:
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
            fullname = signupform.cleaned_data['fullname']
            dob = signupform.cleaned_data['dob']
            email = signupform.cleaned_data['email']
            password1 = signupform.cleaned_data['password1']
            password2 = signupform.cleaned_data['password2']

            if password1 == password2:
                hashed_password = hashlib.sha256(password1.encode()).hexdigest()
                with connection.cursor() as cursor:
                    try:
                        cursor.execute('''INSERT INTO USERS VALUES (USERS_SEQ.NEXTVAL , %s, %s, %s,
                        'dp/default-dp.png', %s, %s)''', [username, hashed_password, email, dob, fullname])
                    except (IntegrityError, DatabaseError) as e:
                        error_message = str(e)
                        if 'USERNAME_UNIQUE' in error_message:
                            error = "username already exists!"
                        elif 'EMAIL_ID_UNIQUE' in error_message:
                            error = "an account has already been created with this email!"
                        elif 'INVALID_DOB' in error_message:
                            error = "invalid date of birth!"
                        else:
                            error = 'failed to sign up, try again later :('
                        return render(request, 'user/signup.html', {'error': error})
                    cursor.execute('SELECT USERS_SEQ.CURRVAL FROM DUAL')
                    id = cursor.fetchone()[0]
                    clear_session(request)
                    request.session['id'] = id
                    request.session['username'] = username
                    request.session['type'] = 'Player'
                    return redirect('feed_detail')
            else:
                return render(request, 'user/signup.html', {'error': 'passwords don\'t match!'})
        else:
            print("Signup Form Error")
            return render(request, 'user/signup.html')

    else:
        #print("Not Post Method")
        return render(request, 'user/signup.html')


def Logout(request):
    try:
        print("Logging Out...")
        print(request.session['id'])
        clear_session(request)
        return HttpResponseRedirect(reverse('login'))
    except:
        print("Logout Error")
        return redirect('my_profile_detail', player_id=request.session['id'])




from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connection
from . import forms
from django.forms.formsets import formset_factory


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
            if authenticate(username, password):
                print("Login Successful")

                # TODO: send to homepage/ Question setter page
                return render(request, 'user/' + pagehtml + '.html')
            else:
                # authentication error
                return render(request, 'user/' + pagehtml + '.html')
        else:
            print("FORM NOT VALID???")
            return render(request, 'user/' + pagehtml + '.html')

    else:
        print(request.method)
        return render(request, 'user/' + pagehtml + '.html')


def authenticate(username, password):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM USERS WHERE USERNAME = %s', [username])
        row = cursor.fetchone()
        if row is not None:
            if row[2] == password:
                return True
            else:
                print("Passowrd doesn't match")
                return False

        else:
            print("No such User")
            return False


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

            print(username, dob, email)

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
        query = '''
            INSERT INTO USERS VALUES (%s , %s, %s, %s, 'abc', %s)
        
        '''

        cursor.execute(query, [total_users + 1, username, password, email, dob])

from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connection
from django.forms.formsets import formset_factory


def abc(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM USERS')
        row = cursor.fetchone()

        name = row[1]
        email = row[3]
        return HttpResponse(name + email)


from django.urls import path
from . import views

urlpatterns = [
    path('<str:master_name>/', views.master_home, name='master_home'),
    path('create/', views.create_quiz, name='create_quiz'),
    path('ajax/show_question/', views.show_questions, name='show_questions'),
]
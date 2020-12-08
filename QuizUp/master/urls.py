from django.urls import path
from . import views

urlpatterns = [
    path('profile/<str:master_name>/', views.master_profile, name='master_profile'),
    path('create/', views.create_quiz, name='create_quiz'),
    path('ajax/show_question/', views.show_questions, name='show_questions'),
    path('ajax/add_topic/', views.add_topic, name='add_topic'),
    path('ajax/check_quiz_title/', views.check_quiz_title, name='check_quiz_title'),
]
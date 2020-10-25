from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/play/', views.play_quiz, name='play_quiz'),
    path('ajax/update_score/', views.update_score, name='update_score'),
]
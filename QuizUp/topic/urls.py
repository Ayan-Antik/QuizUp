from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('ajax/follow/', views.update_follow, name='update_follow'),
]
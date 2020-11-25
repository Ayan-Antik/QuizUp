from django.urls import path
from . import views

urlpatterns = [
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('Feed/', views.feed_detail, name='feed_detail'),
]
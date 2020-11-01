from django.urls import path
from . import views

urlpatterns = [
    path('<int:player_id>/', views.my_profile_detail, name='my_profile_detail'),
    path('ajax/like/', views.update_like, name='update_like'),
    path('ajax/player_follow/', views.update_player_follow, name='update_player_follow'),

]
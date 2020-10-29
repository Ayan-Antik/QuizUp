from django.urls import path
from . import views

urlpatterns = [
    path('profiles/', views.my_profile_detail, name='my_profile_detail'),
    #path('ajax/like/', views.update_like, name='update_like')

]
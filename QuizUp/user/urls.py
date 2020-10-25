from django.urls import path

from . import views

urlpatterns = [
    path('', views.abc, name='abc'),
    path('login/', views.LogIn, name='login'),
    path('Quizmasterlogin/', views.LogIn, name='Quizmasterlogin'),
    path('signup/', views.SignUp, name='signup')
]
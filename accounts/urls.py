
from django.contrib import admin
from django.urls import path, include

from accounts import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('preferences/', views.preferences, name='preferences'),
    #path('mypage/', mypage.as_view(), name='mypage')

]
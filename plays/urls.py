from django.contrib import admin
from django.urls import path
from plays import views

urlpatterns = [
    # <str:pk>로 변경하여 문자열도 받을 수 있게 합니다
    path('play/<str:pk>/', views.play_detail, name='play_detail'),
]
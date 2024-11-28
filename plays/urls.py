from django.contrib import admin
from django.urls import path, include

from plays import views

urlpatterns = [
        path('play/<str:pk>/', views.play_detail, name='play_detail'),
]
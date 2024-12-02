from django.contrib import admin
from django.urls import path
from plays import views

urlpatterns = [
    path('play/<str:pk>/', views.play_detail, name='play_detail'),
    path('play_review/', views.play_review, name='play_review'),
    path('reviews/<int:review_id>/like/', views.toggle_like, name='toggle_like'),
    path('reviews/<int:review_id>/dislike/', views.toggle_dislike, name='toggle_dislike'),
]
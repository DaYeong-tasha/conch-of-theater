from django.contrib import admin
from django.urls import path
from plays import views
from plays.views import PlayReviewListView

app_name = 'plays'

urlpatterns = [
    path('play/<str:pk>/', views.play_detail, name='play_detail'),
    path('play_review/<str:play_id>/', PlayReviewListView.as_view(), name='play_review'),

    # ListView아닌 버전
    # path('play_review/<str:play_id>/', views.play_review, name='play_review'),

    path('reviews/like/<int:review_id>/', views.toggle_like, name='toggle_like'),
    path('reviews/dislike/<int:review_id>/', views.toggle_dislike, name='toggle_dislike'),

    path('reviews/write/<str:play_id>/', views.write_review, name='write_review'),
    path('review/edit/<str:play_id>/<int:review_id>/', views.edit_review, name='edit_review'),

    path('review/delete/<str:play_id>/<int:review_id>/', views.delete_review, name='delete_review'),
]
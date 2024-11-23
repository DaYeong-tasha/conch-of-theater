from django.contrib import admin
from django.urls import path, include

from reviews.views import ReviewListView

urlpatterns = [
    path('', ReviewListView.as_view(), name='review'),  # 클래스형 뷰로 변경
]
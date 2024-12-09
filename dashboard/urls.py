
from django.contrib import admin
from django.urls import path, include

from dashboard import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard')
]

from django.urls import path, include
from . import views_all, views

urlpatterns = [
    path('', views.home, name='before_login'),
    path('home/', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
]

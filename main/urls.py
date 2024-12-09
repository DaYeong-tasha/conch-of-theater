from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='before_login'),
    path('home/', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('play_rank/', views.play_rank, name='play_rank'),  # 랭킹 화면
    path('play/<str:pk>/', views.get_play_details, name='play_detail'),
]

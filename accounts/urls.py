
from django.contrib import admin
from django.urls import path, include

from accounts import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('check-id/', views.check_id, name='check_id'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.mypage_home, name='profile'),
    path('profile/load_content/<str:tab_name>/', views.load_tab_content, name='load_tab_content'),  # 탭 콘텐츠 로드
    path('profile/edit/', views.mypage_update, name='mypage_update'),

]

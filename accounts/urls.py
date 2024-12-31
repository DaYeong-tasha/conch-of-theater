
from django.contrib import admin
from django.urls import path, include

from accounts import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('check-id/', views.check_id, name='check_id'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    #path('profile/', views.mypage_home, name='profile'),
    path('profile/load_content/<str:tab_name>/', views.load_tab_content, name='load_tab_content'),  # 탭 콘텐츠 로드
    path('profile/edit/', views.mypage_update, name='mypage_update'),
    path('profile/reviews/list/', views.mypage_reviews_list, name='profile_reviews_list'),
    path('profile/reviews/edit/<int:review_id>/', views.reviews_edit, name='profile_reviews_edit'),
    path('profile/reviews/delete/<int:review_id>/', views.delete_review, name='profile_reviews_delete'),
    path('profile/favorites/', views.mypage_favorites, name='profile_favorites'),
    path('profile/favorites/remove_from_favorites/<str:play_id>/', views.remove_from_favorites, name='remove_from_favorites'),
]





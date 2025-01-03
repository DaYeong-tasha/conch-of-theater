from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='before_login'),
    path('home/', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    #path('play_rank/', views.play_rank, name='play_rank'),  # 랭킹 화면
    # 추천 연극 데이터를 반환하는 API 엔드포인트
    path('play/<str:play_id>/', views.get_user_recommendations, name='play_detail'),
    path('recommend_plays/', views.recommend_plays, name='recommend_plays'),
    # 메인페이지 버튼 관련
    # path('filter_plays/<str:status>/', FilterPlaysView.as_view(), name='filter_plays'),
    path('filter_plays/', views.filter_plays, name='filter_plays'),
]

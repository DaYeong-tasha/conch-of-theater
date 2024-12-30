from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from reviews import views
from reviews.views import ReviewListView

urlpatterns = [
    path('', ReviewListView.as_view(), name='review'),  # 클래스형 뷰로 변경
    path('review/write/', views.review_write, name='review_write'),
    path('review/<int:pk>/', views.review_detail, name='review_detail'),
    path('review/edit/<int:pk>/', views.review_edit, name='review_edit'),
    path('review/delete/<int:pk>/', views.review_delete, name='review_delete'),
]
# Debug Toolbar 활성화
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
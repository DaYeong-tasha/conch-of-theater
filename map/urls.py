from django.urls import path
from . import views

app_name = 'map'
urlpatterns = [
    path('', views.theater_map_view, name='theater_map'), 
]
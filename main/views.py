from django.contrib.auth import logout
from django.shortcuts import render, redirect


# Create your views here.

def home(request):
    if request.user.is_authenticated:  # 로그인 여부 (o)
        return render(request, 'main/home.html')  # 로그인 후 템플릿
    else:
        return render(request, 'main/before_login.html')  # 로그인 전 템플릿

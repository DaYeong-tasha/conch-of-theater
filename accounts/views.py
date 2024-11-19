from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView

from common.models import Users
from .forms import LoginForm

# 커스텀한 User 모델의 구성요소
# username = 유저 아이디
# fullname = 유저 이름 ex.홍길동
# address = 주소
# birth = 생년월일
# email	이메일
# password	암호화된 비밀번호
# is_staff	admin접속 가능 여부
# is_activate	계정 활성 여부
# is_superuser	모든 권한 활성 여부
# last_login	마지막으로 로그인한 시간
# date_joined	계정이 생성된 날짜

def register(request):
    if request.method == 'POST':
        res_data = {}  # 프론트에 던져줄 응답 데이터
        if request.POST.get('password') != request.POST.get('confirm-password'):
            res_data['error'] = "비밀번호가 다릅니다."
            # 패스워드 확인 오류 메시지
            return redirect('register')
        else:
            username = request.POST.get('username', None)
            fullname = request.POST.get('fullname', None)
            password = request.POST.get('password', None)

            email_local = request.POST.get('email_local', None)
            email_select = request.POST.get('email_select', None)
            email_input = request.POST.get('email_input', None)
            email_domain = email_input if email_select == 'custom' else email_select
            email = f"{email_local}@{email_domain}"

            address = request.POST.get('address', None)
            birth = request.POST.get('birth', None)  # 연령대 따로 계산해야 함.
            gender = request.POST.get('gender', None)

            # 장르 및 키워드 다중 선택 처리
            my_genre = request.POST.getlist('my_genre', None)  # 리스트로 받아옴
            my_play_mood = request.POST.getlist('my_play_mood', None)  # 추가
            my_keyword = request.POST.getlist('my_keyword', None)
            my_actor = request.POST.get('my_actor', None)  # 수정: 'my_act' -> 'my_actor'

            user = Users(
                username=username,
                fullname=fullname,
                password=password,
                email=email,
                address=address,
                birth=birth,
                gender=gender,
                # 이 부분을 삭제해서 하는 가ㅓ
                my_genre=my_genre,
                my_play_mood=my_play_mood,
                my_keyword=my_keyword,
                my_actor=my_actor,
            )

            user.set_password(password)  # 비밀번호 암호화
            user.save()

        # 세션에 user_id 저장
        request.session['user_id'] = user.user_id  # 여기 추가
        # user.session.에스큐엘이랑 확인 필요.  세션 어디로들어가는 지 모르겠음.

        # 회원가입 완료 후 선호 설정 페이지로 리디렉션
        messages.success(request, '선호 설정을 진행해주세요.')
        return redirect('preferences') # 선호 설정 페이지로 이동

    elif request.method == 'GET':
        return render(request, 'accounts/register.html')
    else:
        return render(request, 'accounts/register.html')


# 선호 설정 페이지
def preferences(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')  # 기본 정보가 저장되지 않으면 첫 번째 페이지로 리디렉션

    user = Users.objects.get(id=user_id)  # 세션에서 사용자 정보 가져오기

    if request.method == 'POST':
        # 선호 정보 처리
        my_genre = request.POST.getlist('my_genre[]')  # 복수 선택된 장르
        my_play_mood = request.POST.getlist('my_play_mood[]')  # 복수 선택된 연극 분위기
        my_play_keyword = request.POST.getlist('my_play_keyword[]')  # 복수 선택된 키워드
        my_actor = request.POST.get('my_actor')  # 배우 (한 명 또는 없을 수도 있음)

        # 선호 정보 업데이트
        user.my_genre = my_genre
        user.my_play_mood = my_play_mood
        user.my_play_keyword = my_play_keyword
        user.my_actor = my_actor
        user.save()  # 사용자 선호 정보 저장

        messages.success(request, '회원가입이 완료되었습니다.')  # 수정된 메시지
        return redirect('login')  # 수정: 로그인 페이지가 아닌 메인 페이지로 리디렉션

    return render(request, 'accounts/preferences.html', {
        'my_genre': user.my_genre,
        'my_play_mood': user.my_play_mood,
        'my_play_keyword': user.my_play_keyword,
        'my_actor': user.my_actor
    })

def user_login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    elif request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)  # 로그인 처리
                messages.success(request, f'안녕하세요 {username.title()}님,')
                messages.success(request, '방문해주셔서 감사합니다!')
                return redirect('home_logged_in')  # 로그인된 메인페이지로 리다이렉트

        # 유효하지 않거나 사용자가 인증 되지 않을 경우
        messages.error(request, '잘못된 사용자 ID나 비밀번호입니다')
        return render(request, 'accounts/login.html', {'form': form})


# 로그인 후 메인 페이지
def home(request):
    return render(request, 'main/home.html')


def user_logout(request):
    logout(request)
    messages.success(request, '로그아웃 되셨습니다.')
    messages.success(request, '좋은 하루 보내세요 :)')
    return redirect('before_login')

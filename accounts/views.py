from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from common.models import Users
from .forms import LoginForm, UserProfileForm
from django.db import transaction



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
        try:
            with transaction.atomic():  # 트랜잭션으로 묶기
                # 사용자 기본 정보 처리
                username = request.POST.get('username')
                fullname = request.POST.get('fullname')
                password = request.POST.get('password')
                email_local = request.POST.get('email_local')
                email_select = request.POST.get('email_select')
                email_input = request.POST.get('email_input')
                email_domain = email_input if email_select == 'custom' else email_select
                if not email_local or not email_domain:
                    raise ValidationError('이메일을 정확히 입력해주세요.')
                email = f"{email_local}@{email_domain}"

                if Users.objects.filter(username=username).exists():
                    raise IntegrityError(f"'{username}'은 이미 존재하는 아이디입니다.")

                address = request.POST.get('address')
                birth = request.POST.get('birth')
                gender = request.POST.get('gender')

                # 사용자 생성
                user = Users(
                    username=username,
                    fullname=fullname,
                    email=email,
                    address=address,
                    birth=birth,
                    gender=gender,
                )
                user.set_password(password)

                # 선호도 데이터 저장
                user.my_genre = request.POST.getlist('my_genre[]')
                user.my_play_mood = request.POST.getlist('my_play_mood[]')
                user.my_play_keyword = request.POST.getlist('my_play_keyword[]')
                user.my_actor = request.POST.get('my_actor') or "없음"

                user.save()

                # 메시지 및 리다이렉트
                messages.success(request, '회원가입이 완료되었습니다! 로그인을 진행해주세요.')
                return redirect('login')
        except ValidationError as ve:
            messages.error(request, str(ve))
        except IntegrityError as ie:
            messages.error(request, str(ie))
        except Exception as e:
            messages.error(request, '회원가입 중 예상치 못한 오류가 발생했습니다.')
    return render(request, 'accounts/register.html')



def check_id(request):
    user_id = request.GET.get('id')
    if user_id:
        # 중복된 아이디가 있는지 확인
        exists = Users.objects.filter(username=user_id).exists()  # 수정된 부분
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})

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
                return redirect('home')  # 로그인 후 이동할 페이지 설정

        # 유효하지 않거나 인증되지 않은 사용자 처리
        messages.error(request, '잘못된 사용자 ID나 비밀번호입니다.')
        return render(request, 'accounts/login.html', {'form': form})


# 로그인 후 메인 페이지
def home(request):
    return redirect('home')


def user_logout(request):
    logout(request)
    messages.success(request, '로그아웃 되셨습니다.')
    messages.success(request, '좋은 하루 보내세요 :)')
    return redirect('before_login')



#회원정보 조회
@login_required
def mypage_home(request):
    try:
        user_profile = Users.objects.get(username=request.user.username)
    except Users.DoesNotExist:
        messages.error(request, '사용자 프로필을 찾을 수 없습니다.')  # 사용자 프로필 없음 오류 메시지
        return redirect('profile')  # 프로필이 없으면 마이페이지로 리디렉션

    return render(request, 'accounts/profile.html', {'user_profile': user_profile})


class FavoritePlay:
    pass


@login_required
def load_tab_content(request, tab_name):
    try:
        user_profile = Users.objects.get(username=request.user.username)
    except Users.DoesNotExist:
        user_profile = None

    if tab_name == 'profile':
        content = render_to_string('accounts/profile_edit.html', {'user_profile': user_profile})
    elif tab_name == 'favorites':
        # 즐겨찾기 데이터를 가져옵니다. 예를 들어 'FavoritePlay' 모델에서 즐겨찾기를 가져온다고 가정
        favorites = FavoritePlay.objects.filter(user=user_profile)
        content = render_to_string('accounts/profile_favorites.html', {'favorites': favorites})
    elif tab_name == 'reviews':
        content = render_to_string('accounts/profile_reviews_list.html', {'user_profile': user_profile})
    elif tab_name == 'dashboard':
        content = render_to_string('accounts/profile_dashboard.html', {'user_profile': user_profile})
    else:
        content = "Invalid tab"

    return JsonResponse({'content': content})


#회원정보 수정
@login_required
def mypage_update(request):
    try:
        user_profile = Users.objects.get(username=request.user.username)
    except Users.DoesNotExist:
        user_profile = None
        messages.error(request, '사용자 프로필을 찾을 수 없습니다.')  # 사용자 프로필 없음 오류 메시지
        return redirect('accounts:mypage_home')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, '회원 정보가 성공적으로 수정되었습니다.')  # 성공 메시지
            # 수정이 완료되면 마이페이지로 리다이렉트
            return redirect('profile') # 서버에서 리디렉션 처리
        else:
            messages.error(request, '입력한 정보에 오류가 있습니다.')  # 오류 메시지
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'accounts/profile_edit.html', {'form': form, 'user_profile': user_profile})




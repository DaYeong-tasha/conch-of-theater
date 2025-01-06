from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from accounts.models import Users
from django.db import transaction
from .forms import ReviewForm, LoginForm, UserProfileForm
from common.models import Review, Play_list, Play_detail
from django.db.models import Q


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

                # 리다이렉트
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

    if tab_name == 'mypage_update':
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
'''
def mypage_update(request):
    try:
        user_profile = Users.objects.get(username=request.user.username)
    except Users.DoesNotExist:
        messages.error(request, '사용자 프로필을 찾을 수 없습니다.')
        return redirect('home')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            # ManyToManyField 및 JSONField 데이터 처리
            user = form.save(commit=False)

            # JSONField 및 CharField 처리
            user.my_play_keyword = form.cleaned_data.get('my_play_keyword') or []  # 선택된 키워드
            #user.my_actor = form.cleaned_data.get('my_actor') or "없음"  # 선택된 배우 (없으면 기본값)

            user.save()  # 수정된 데이터 저장
            form.save_m2m()  # ManyToMany 관계 저장
            messages.success(request, '회원 정보가 성공적으로 수정되었습니다.')
            return redirect('home')
        else:
            print("폼 에러:", form.errors)  # 에러 출력
            messages.error(request, '정보 수정에 실패했습니다.')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})
'''


@login_required
def mypage_update(request):
    try:
        user_profile = Users.objects.get(username=request.user.username)  # Users 모델로부터 사용자 가져오기
    except Users.DoesNotExist:
        messages.error(request, '사용자 프로필을 찾을 수 없습니다.')
        return redirect('accounts:mypage_home')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            # ManyToManyField 및 JSONField 데이터 처리
            user = form.save(commit=False)

            # JSONField 및 CharField 처리
            user.my_play_keyword = form.cleaned_data.get('my_play_keyword') or []  # 선택된 키워드
            user.my_genre = form.cleaned_data.get('my_genre') or ""  # 선호 장르 처리 (콤마로 저장)

            user.save()  # 수정된 데이터 저장
            form.save_m2m()  # ManyToMany 관계 저장
            messages.success(request, '회원 정보가 성공적으로 수정되었습니다.')
            return redirect('profile')
        else:
            print("폼 에러:", form.errors)  # 에러 출력
            messages.error(request, '정보 수정에 실패했습니다.')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})




#my리뷰
@login_required
def mypage_reviews_list(request):
    # 현재 사용자가 작성한 리뷰만 가져오기
    user_reviews = Review.objects.filter(username=request.user.username).order_by('-review_reg_date')
    return render(request, 'accounts/profile_reviews_list.html', {'user_reviews': user_reviews})



# 리뷰 리스트 삭제
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, review_id=review_id)  # review_id로 가져오기

    # 해당 리뷰가 현재 사용자의 것인지 확인 (보안)
    if review.username == request.user:  # username으로 확인
            review.delete()  # 리뷰 삭제
            messages.success(request, "리뷰가 성공적으로 삭제되었습니다.")
    else:
            messages.error(request, "리뷰를 삭제할 권한이 없습니다.")
    return redirect('profile_reviews_list')

    messages.error(request, "잘못된 요청입니다.")
    return redirect('profile_reviews_list')


#리뷰 수정
@login_required
def reviews_edit(request, review_id):
    review = get_object_or_404(Review, review_id=review_id, username=request.user.username)  # 해당 리뷰 가져오기

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()  # 수정된 데이터 저장
            messages.success(request, "수정되었습니다.")
            return redirect('profile_reviews_list')  # 수정 후 리뷰 리스트로 리다이렉트
    else:
        form = ReviewForm(instance=review)  # 기존 데이터로 폼 채우기

    return render(request, 'accounts/profile_reviews_edit.html', {'form': form})  # 수정 페이지 렌더링


#즐겨찾기♡
def mypage_favorites(request):
    # 현재 로그인한 사용자의 즐겨찾기한 연극 목록을 가져옵니다.
    favorite_plays = Play_list.objects.filter(favorite_users=request.user)

    # get_play_details() 함수에서 필요한 데이터를 가져옵니다.
    play_details = get_play_details()

    # favorite_plays에 play_details 값을 추가합니다.
    for play in favorite_plays:
        # play_details에서 해당 play의 상세 정보를 찾아서 play에 추가합니다.
        matching_detail = next((detail for detail in play_details if detail['play_id'] == play.play_id), None)
        if matching_detail:
            play.details = matching_detail  # play 객체에 play_details를 추가 (임시 필드)

    context = {
        'favorite_plays': favorite_plays
    }
    return render(request, 'accounts/profile_favorites.html', context)

def get_play_details():
    """공연중 또는 공연 예정인 Play_detail 데이터를 가져오기 (최적화)"""
    return Play_detail.objects.filter(
        Q(play_status='공연중') | Q(play_status='공연예정')
    ).values(
        'play_id', 'play_name', 'play_poster',
        'play_strdate', 'play_enddate', 'play_status', 'theater_nm'
    )


def remove_from_favorites(request, play_id):
    if request.user.is_authenticated:
        play = get_object_or_404(Play_list, pk=play_id)
        # 즐겨찾기에서 제거하는 로직 추가
        play.favorite_users.remove(request.user)
        return redirect('accounts:profile_favorites')  # 즐겨찾기 페이지로 리디렉션
    return redirect('login')



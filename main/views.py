from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F, Q, FloatField
from django.db.models.functions import Cast
from COT import settings
from common.models import Play_detail, Play_rank
from accounts.models import Users  # Users 모델 추가
from map.views import get_theaters_data

# 지역 매핑
LOC_MAPPING = {
    "서울특별시": "서울", "부산광역시": "경상", "대구광역시": "경상",
    "인천광역시": "경기", "광주광역시": "전라", "대전광역시": "충청",
    "울산광역시": "경상", "세종특별자치시": "충청", "경기도": "경기",
    "강원도": "강원", "충청북도": "충청", "충청남도": "충청",
    "전라북도": "전라", "전라남도": "전라", "경상북도": "경상",
    "경상남도": "경상", "제주특별자치도": "제주"
}

def get_user_recommendations(user):
    """사용자 추천 필터링 로직"""
    if not user.is_authenticated:
        return []

    try:
        # Users 모델에서 사용자 정보 가져오기
        user_obj = Users.objects.get(username=user.username)
    except Users.DoesNotExist:
        return []

    # 사용자 정보
    user_loc = LOC_MAPPING.get(user_obj.address, None)
    print(f"Mapped location: {user_loc}")

    # play_ranks에서 link_area 필드 값들을 필터링
    play_ranks = Play_rank.objects.filter(ststypes="month")

    # '대학로'는 '서울'로 매핑하고, '전국'은 무시
    for play in play_ranks:
        if play.link_area == '대학로':
            play.link_area = '서울'
        elif play.link_area == '전국':
            play.link_area = None  # '전국'은 필터링에서 제외

    # 예시 디버깅 코드
    print(f"Before region filter: {play_ranks.count()} records")

    # 지역 필터
    if user_loc:
        play_ranks = play_ranks.filter(link_area=user_loc)
        print(f"After region filter: {play_ranks.count()} records")

    # 연극 필터링
    play_ids = play_ranks.values_list('play_id', flat=True)
    recommendations = Play_detail.objects.filter(play_id__in=play_ids)

    # 장르 필터
    if user_obj.my_genre:
        recommendations = recommendations.filter(genre__in=user_obj.my_genre)
        print(f"After genre filter: {recommendations.count()} records")

    # 성별 필터 # 값이 float라서 비교해서 바꿔야 함.
    if user_obj.gender in ['남성', '여성']:
        gender_field = 'male' if user_obj.gender == '남성' else 'female'
        recommendations = recommendations.annotate(
            male_float=Cast('male', FloatField()),
            female_float=Cast('female', FloatField())
        )
        recommendations = recommendations.filter(
            **{f"{gender_field}__gt": F('female' if gender_field == 'male' else 'male')})
        print(f"After gender filter: {recommendations.count()} records")

    # 연령대 필터
    recommendations = recommendations.annotate(
        teenage_float=Cast('teenage', FloatField()),
        twenty_float=Cast('twenty', FloatField()),
        thirty_float=Cast('thirty', FloatField()),
        forty_float=Cast('forty', FloatField()),
        fifty_float=Cast('fifty', FloatField())
    )
    print(f"User age: {2025 - user_obj.birth.year}")  # 사용자 나이 출력

    if user_obj.birth.year and (2025 - user_obj.birth.year) < 20:
        recommendations = recommendations.filter(teenage_float__gt=0)
        print(f"After teenage filter: {recommendations.count()} records")
    elif (2025 - user_obj.birth.year) < 30:
        recommendations = recommendations.filter(twenty_float__gt=0)
        print(f"After twenty filter: {recommendations.count()} records")
    elif (2025 - user_obj.birth.year) < 40:
        recommendations = recommendations.filter(thirty_float__gt=0)
        print(f"After thirty filter: {recommendations.count()} records")
    elif (2025 - user_obj.birth.year) < 50:
        recommendations = recommendations.filter(forty_float__gt=0)
        print(f"After forty filter: {recommendations.count()} records")
    else:
        recommendations = recommendations.filter(fifty_float__gt=0)
        print(f"After fifty filter: {recommendations.count()} records")

    return recommendations.values(
        'play_id', 'play_name', 'play_poster',
        'play_strdate', 'play_enddate', 'play_status', 'theater_nm'
    )

def recommend_plays(request):
    """추천 연극 데이터를 JSON 형태로 반환"""
    if not request.user.is_authenticated:
        return JsonResponse({"play_details": []}, safe=False)

    recommended_plays = get_user_recommendations(request.user)  # 기존 추천 함수 호출
    return JsonResponse({"play_details": list(recommended_plays)}, safe=False)

def home(request):
    """홈 화면"""
    # 사용자 맞춤 추천 데이터
    user_recommendations = get_user_recommendations(request.user)

    # 극장 데이터
    theater_context = get_theaters_data()
    theaters = theater_context.get('theaters', [])

    context = {
        'theaters': theaters,
        'kakao_map_api_key': settings.KAKAO_MAP_API_KEY,
        'play_details': user_recommendations,
    }

    # 로그인 상태에 따라 템플릿 선택
    template_name = 'main/home.html' if request.user.is_authenticated else 'main/before_login.html'
    return render(request, template_name, context)


def filter_plays(request):
    status = request.GET.get('status', '전체')
    genre = request.GET.get('genre', '전체')
    keyword = request.GET.get('keyword', '전체')
    gender = request.GET.get('gender', '전체')
    age = request.GET.get('age', '전체')
    openrun = request.GET.get('openrun', '전체')
    limit = 200  # 기본값 200
    page = int(request.GET.get('page', 1))  # 페이지 번호, 기본값 1

    play_details = Play_detail.objects.all().order_by('-play_enddate')

    if status != '전체':
        status_list = status.split(',')
        play_details = play_details.filter(play_status__in=status_list)
    if openrun == 'Y':
        play_details = play_details.filter(openrun='Y')

    if genre != '전체':
        genre_list = genre.split(',')
        play_details = play_details.filter(genre__in=genre_list)
    if keyword != '전체':
        keyword_list = keyword.split(',')
        for kw in keyword_list:
            play_details = play_details.filter(home_keyword__icontains=kw)
    if gender != '전체':
        if gender == '남성':
            play_details = play_details.filter(male__gt=F('female'))
        elif gender == '여성':
            play_details = play_details.filter(female__gt=F('male'))
    if age != '전체':
        age_list = age.split(',')
        play_details = play_details.annotate(
            teenage_float=Cast('teenage', FloatField()),
            twenty_float=Cast('twenty', FloatField()),
            thirty_float=Cast('thirty', FloatField()),
            forty_float=Cast('forty', FloatField()),
            fifty_float=Cast('fifty', FloatField())
        )
        age_filters = Q()
        for age_group in age_list:
            if age_group == '10대':
                age_filters |= Q(teenage_float__gt=0)
            elif age_group == '20대':
                age_filters |= Q(twenty_float__gt=0)
            elif age_group == '30대':
                age_filters |= Q(thirty_float__gt=0)
            elif age_group == '40대':
                age_filters |= Q(forty_float__gt=0)
            elif age_group == '50대+':
                age_filters |= Q(fifty_float__gt=0)
        play_details = play_details.filter(age_filters)

    offset = (page - 1) * limit
    play_details = play_details[offset:offset + limit]  # 페이지에 따른 개수 제한

    play_details_list = list(play_details.values('play_id', 'play_name', 'play_poster', 'play_strdate', 'play_enddate', 'play_status', 'theater_nm'))
    return JsonResponse({'play_details': play_details_list})

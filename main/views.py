from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F, Q, FloatField
from django.db.models.functions import Cast
from COT import settings
from common.models import Play_detail, Play_rank
from accounts.models import Users  # Users 모델 추가
from map.views import get_theaters_data

# 지역 매핑
# LOC_MAPPING = {
#     "서울특별시": "서울",
#     "경기도": "경기",
#     "인천광역시": "경기",
#     "부산광역시": "경상",
#     "대구광역시": "경상",
#     "울산광역시": "경상",
#     "경상북도": "경상",
#     "경상남도": "경상",
#     "광주광역시": "전라",
#     "전라남도": "전라",
#     "전라북도": "전라",
#     "대전광역시": "충청",
#     "세종특별자치시": "충청",
#     "충청북도": "충청",
#     "충청남도": "충청",
#     "강원도": "강원",
#     "제주특별자치도": "제주"
# }
from django.db.models import FloatField
from django.db.models.functions import Cast


def get_user_recommendations(user):
    if not user.is_authenticated:
        return []

    try:
        user_obj = Users.objects.get(username=user.username)
    except Users.DoesNotExist:
        return []

    recommendations = Play_detail.objects.filter(
        play_status__in=["공연중", "공연예정"]  # 공연 상태 필터
    )
    print(f"After play status filter: {recommendations.count()} records")

    # Play_detail의 loc 값들을 가져오고 distinct로 필터링
    loc_values = list(Play_detail.objects.values_list('loc', flat=True).distinct())
    print(f"Distinct loc values: {loc_values}")

    # 사용자의 주소값 (user_loc) 설정
    user_loc = user_obj.address
    print(f"User address: {user_loc}")

    # 지역 필터링
    if user_loc and user_loc in loc_values:
        recommendations = recommendations.filter(loc=user_loc)
    else:
        print(f"No matching location found for user address: {user_loc}")

    print(f"After region filter: {recommendations.count()} records")

    # 장르 필터 (my_genre는 여러 개의 장르가 있을 수 있음)
    print(f"Applying genre filter for: {user_obj.my_genre}")
    if user_obj.my_genre:
        # 장르를 ','로 분리
        user_genres = [genre.strip() for genre in user_obj.my_genre[0].split(',')]
        print(f"User selected genres: {user_genres}")

        recommendations = recommendations.filter(genre__in=user_genres)
    print(f"After genre filter: {recommendations.count()} records")


    # 성별 필터
    if user_obj.gender in ['남성', '여성']:
        gender_field = 'male' if user_obj.gender == '남성' else 'female'
        print(f"Applying gender filter for {user_obj.gender} -> {gender_field}")
        recommendations = recommendations.annotate(
            gender_value=Cast(gender_field, FloatField())
        ).filter(gender_value__gt=0.0)
        print(f"Recommendations after gender filter: {recommendations.count()} records")

    # 연령대 필터
    recommendations = recommendations.annotate(
        teenage_float=Cast('teenage', FloatField()),
        twenty_float=Cast('twenty', FloatField()),
        thirty_float=Cast('thirty', FloatField()),
        forty_float=Cast('forty', FloatField()),
        fifty_float=Cast('fifty', FloatField())
    )
    user_age = 2025 - user_obj.birth.year
    print(f"User age: {user_age}")

    if user_age < 20:
        recommendations = recommendations.filter(teenage_float__gt=0)
    elif user_age < 30:
        recommendations = recommendations.filter(twenty_float__gt=0)
    elif user_age < 40:
        recommendations = recommendations.filter(thirty_float__gt=0)
    elif user_age < 50:
        recommendations = recommendations.filter(forty_float__gt=0)
    else:
        recommendations = recommendations.filter(fifty_float__gt=0)
    print(f"After age filter: {recommendations.count()} records")

    # 결과 반환
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

from django.shortcuts import render
from COT import settings
from common.models import Play_detail, Play_rank
from map.views import get_theaters_data
from django.http import JsonResponse
from django.db.models import F, FloatField, Q
from django.db.models.functions import Cast
import datetime

def get_play_details():
    """공연중 또는 공연 예정인 Play_detail 데이터를 가져오기 (최적화)"""
    return Play_detail.objects.filter(
        Q(play_status='공연중') | Q(play_status='공연예정')
    ).values(
        'play_id', 'play_name', 'play_poster',
        'play_strdate', 'play_enddate', 'play_status', 'theater_nm'
    )

# 지역별 코드 매핑 정보
region_groups = {
    "전국": ["11", "41", "28", "43", "44", "30", "47", "48", "27", "26", "31", "45", "46", "29", "51", "50", "UNI"],
    "서울": ["11", "UNI"],
    "경기": ["41", "28"],
    "충청": ["43", "44", "30"],
    "경상": ["47", "48", "27", "26", "31"],
    "전라": ["45", "46", "29"],
    "강원": ["51"],
    "제주": ["50"],
    "대학로": ["UNI"],
}

def map_user_address_to_link_area(address):
    """주소를 link_area에 매핑"""
    mapping = {
        "서울특별시": "서울",
        "부산광역시": "경상",
        "대구광역시": "경상",
        "인천광역시": "경기",
        "광주광역시": "전라",
        "대전광역시": "충청",
        "울산광역시": "경상",
        "세종특별자치시": "충청",
        "경기도": "경기",
        "강원도": "강원",
        "충청북도": "충청",
        "충청남도": "충청",
        "전라북도": "전라",
        "전라남도": "전라",
        "경상북도": "경상",
        "경상남도": "경상",
        "제주특별자치도": "제주",
    }
    return mapping.get(address, "전국")


def calculate_age_group(birth):
    """생년월일로 나이대 계산"""
    # birth가 '10대'와 같은 나이대 문자열인 경우 처리
    if isinstance(birth, str) and birth in ['10대', '20대', '30대', '40대', '50대+']:
        return birth  # 이미 나이대 문자열이므로 그대로 반환

    # birth가 datetime 객체일 경우, 바로 연도를 사용
    if isinstance(birth, datetime.date):
        current_year = datetime.datetime.now().year
        birth_year = birth.year
    else:
        # birth가 문자열 형식인 경우에만 변환
        try:
            birth = datetime.datetime.strptime(birth, "%Y-%m-%d")
            current_year = datetime.datetime.now().year
            birth_year = birth.year
        except ValueError:
            # birth 값이 잘못된 경우, 예외 처리
            raise ValueError("잘못된 생년월일 형식입니다. 'YYYY-MM-DD' 형식이어야 합니다.")

    age = current_year - birth_year

    if age < 20:
        return '10대'
    elif 20 <= age < 30:
        return '20대'
    elif 30 <= age < 40:
        return '30대'
    elif 40 <= age < 50:
        return '40대'
    else:
        return '50대+'


def filter_by_age_group(queryset, age_group, gender=None):
    """나이대와 성별에 따라 필터링하는 함수"""
    filters = Q()

    # 나이대 필터링
    if age_group == '10대':
        filters &= Q(teenage__gt=F('twenty')) & Q(teenage__gt=F('thirty')) & Q(teenage__gt=F('forty')) & Q(
            teenage__gt=F('fifty'))
    elif age_group == '20대':
        filters &= Q(twenty__gt=F('teenage')) & Q(twenty__gt=F('thirty')) & Q(twenty__gt=F('forty')) & Q(
            twenty__gt=F('fifty'))
    elif age_group == '30대':
        filters &= Q(thirty__gt=F('teenage')) & Q(thirty__gt=F('twenty')) & Q(thirty__gt=F('forty')) & Q(
            thirty__gt=F('fifty'))
    elif age_group == '40대':
        filters &= Q(forty__gt=F('teenage')) & Q(forty__gt=F('twenty')) & Q(forty__gt=F('thirty')) & Q(
            forty__gt=F('fifty'))
    elif age_group == '50대+':
        filters &= Q(fifty__gt=F('teenage')) & Q(fifty__gt=F('twenty')) & Q(fifty__gt=F('thirty')) & Q(
            fifty__gt=F('forty'))

    # 성별 필터링
    if gender == 'male':
        filters &= Q(male='1')
    elif gender == 'female':
        filters &= Q(female='1')

    return queryset.filter(filters)


def apply_filters(queryset, status, genre, gender, birth):
    """필터링을 적용하는 함수"""
    # 사용자 나이대 계산
    age_group = calculate_age_group(birth) if birth else None

    # 장르 필터링
    if genre and genre != '전체':
        queryset = queryset.filter(play_detail__genre=genre)  # play_detail 테이블에서 genre 참조

    # 성별 필터링
    if gender and gender != '기타':
        if gender == '남성':
            queryset = queryset.filter(male__gt=F('female'))
        elif gender == '여성':
            queryset = queryset.filter(female__gt=F('male'))

    # 나이대 필터링 적용
    if age_group:
        queryset = filter_by_age_group(queryset, age_group, gender)

    return queryset


def home(request):
    # 기본 데이터 가져오기
    play_details = get_play_details()
    theater_context = get_theaters_data()
    theaters = theater_context.get('theaters', [])

    # 사용자 정보 가져오기
    user_address = request.user.address if request.user.is_authenticated else None
    user_genre = request.user.my_genre if request.user.is_authenticated else '전체'  # User 모델에서 가져오기
    user_gender = request.user.gender if request.user.is_authenticated else '기타'
    user_birth = request.user.birth if request.user.is_authenticated else None
    link_area = map_user_address_to_link_area(user_address) if user_address else "전국"
    age_group = calculate_age_group(user_birth) if user_birth else None

    # Play_rank에서 추천 데이터 가져오기 (랭킹 기준)
    recommended_plays = Play_rank.objects.filter(
        rank_area=link_area,
        ststypes='month',  # 월간 랭킹
    )

    # 필터 적용
    recommended_plays = apply_filters(
        recommended_plays, user_genre, '전체', user_gender, age_group
    )

    # 추천 데이터 상위 10개 가져오기
    recommended_plays = recommended_plays.values(
        'play_id', 'play_name', 'play_poster', 'rank', 'theater_nm'
    ).order_by('rank')[:10]

    # Play_detail에서 최신 50개 가져오기 (play_enddate 기준)
    play_details = Play_detail.objects.all().order_by('-play_enddate')[:50]

    # context에 필요한 데이터만 포함시켜서 전달
    context = {
        'theaters': theaters,
        'kakao_map_api_key': settings.KAKAO_MAP_API_KEY,
        'play_details': play_details,
        'recommended_plays': recommended_plays,
        'user_genre': user_genre,  # 템플릿에서 사용할 수 있도록 전달
        'user_gender': user_gender,  # 템플릿에서 사용할 수 있도록 전달
        'age_group': age_group,  # 템플릿에서 사용할 수 있도록 전달
    }

    # 로그인 여부에 따라 적절한 템플릿 렌더링
    template_name = 'main/home.html' if request.user.is_authenticated else 'main/before_login.html'
    return render(request, template_name, context)


def filter_plays(request):
    status = request.GET.get('status', '전체')
    genre = request.GET.get('genre', '전체')
    keyword = request.GET.get('keyword', '전체')
    gender = request.GET.get('gender', '전체')
    age = request.GET.get('age', '전체')

    play_details = Play_detail.objects.all().order_by('-play_enddate')

    if status != '전체':
        play_details = play_details.filter(play_status=status)
    if genre != '전체':
        play_details = play_details.filter(genre=genre)
    if keyword != '전체':
        play_details = play_details.filter(home_keyword__icontains=keyword)
    if gender != '전체':
        if gender == '남성':
            play_details = play_details.filter(male__gt=F('female'))
        elif gender == '여성':
            play_details = play_details.filter(female__gt=F('male'))
    if age != '전체':
        play_details = play_details.annotate(
            teenage_float=Cast('teenage', FloatField()),
            twenty_float=Cast('twenty', FloatField()),
            thirty_float=Cast('thirty', FloatField()),
            forty_float=Cast('forty', FloatField()),
            fifty_float=Cast('fifty', FloatField())
        )
        if age == '10대':
            play_details = play_details.filter(
                Q(teenage_float__gt=F('twenty_float')) &
                Q(teenage_float__gt=F('thirty_float')) &
                Q(teenage_float__gt=F('forty_float')) &
                Q(teenage_float__gt=F('fifty_float'))
            )
        elif age == '20대':
            play_details = play_details.filter(
                Q(twenty_float__gt=F('teenage_float')) &
                Q(twenty_float__gt=F('thirty_float')) &
                Q(twenty_float__gt=F('forty_float')) &
                Q(twenty_float__gt=F('fifty_float'))
            )
        elif age == '30대':
            play_details = play_details.filter(
                Q(thirty_float__gt=F('teenage_float')) &
                Q(thirty_float__gt=F('twenty_float')) &
                Q(thirty_float__gt=F('forty_float')) &
                Q(thirty_float__gt=F('fifty_float'))
            )
        elif age == '40대':
            play_details = play_details.filter(
                Q(forty_float__gt=F('teenage_float')) &
                Q(forty_float__gt=F('twenty_float')) &
                Q(forty_float__gt=F('thirty_float')) &
                Q(forty_float__gt=F('fifty_float'))
            )
        elif age == '50대+':
            play_details = play_details.filter(
                Q(fifty_float__gt=F('teenage_float')) &
                Q(fifty_float__gt=F('twenty_float')) &
                Q(fifty_float__gt=F('thirty_float')) &
                Q(fifty_float__gt=F('forty_float'))
            )

    play_details_list = list(play_details.values('play_id', 'play_name', 'play_poster', 'play_strdate', 'play_enddate', 'play_status', 'theater_nm'))
    return JsonResponse({'play_details': play_details_list})

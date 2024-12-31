from django.shortcuts import render
from COT import settings
from common.models import Play_detail
from map.views import get_theaters_data
from django.http import JsonResponse
from django.db.models import F, FloatField, Q
from django.db.models.functions import Cast
import logging


def get_play_details():
    """공연중 또는 공연 예정인 Play_detail 데이터를 가져오기 (최적화)"""
    # 필드만 필요한 값들로 제한하고, 쿼리셋을 최적화
    return Play_detail.objects.filter(
        Q(play_status='공연중') | Q(play_status='공연예정')
    ).only(
        'play_id', 'play_name', 'play_poster',
        'play_strdate', 'play_enddate', 'play_status', 'theater_nm'
    )


# 지역 매핑 정의
LOC_MAPPING = {
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
    "제주특별자치도": "제주"
}


def home(request):
    """홈 화면 최적화"""
    # 지역 필터링 추가
    selected_area = request.GET.get('link_area', '전체')

    # 지역 그룹으로 필터링
    if selected_area != '전체':
        filtered_play_details = Play_detail.objects.filter(
            play_status__in=['공연중', '공연예정'],
            loc__in=[key for key, value in LOC_MAPPING.items() if value == selected_area]
        )
    else:
        filtered_play_details = Play_detail.objects.filter(play_status__in=['공연중', '공연예정'])

    # 극장 데이터 가져오기
    theater_context = get_theaters_data()

    # 극장 데이터 유효성 검증 및 추출
    theaters = theater_context.get('theaters', [])

    # 중복 지역을 제거한 값만 전달하도록 수정
    context = {
        'theaters': theaters,
        'kakao_map_api_key': settings.KAKAO_MAP_API_KEY,
        'play_details': filtered_play_details,
        'link_area': list(set(LOC_MAPPING.values())),  # 중복 제거된 지역 목록
        'selected_area': selected_area,
    }

    # 로그인 여부에 따라 적절한 템플릿 렌더링
    template_name = 'main/home.html' if request.user.is_authenticated else 'main/before_login.html'
    return render(request, template_name, context)


logger = logging.getLogger(__name__)


def filter_plays(request):
    status = request.GET.get('status', '전체')
    genre = request.GET.get('genre', '전체')
    keyword = request.GET.get('keyword', '전체')
    gender = request.GET.get('gender', '전체')
    age = request.GET.get('age', '전체')
    openrun = request.GET.get('openrun', '전체')
    limit = int(request.GET.get('limit', 300))  # 기본값 10

    # 기본적으로 '공연중'이나 '공연예정' 상태의 데이터를 가져옵니다.
    play_details = Play_detail.objects.all()

    # 필터 조건 적용
    if status != '전체':
        status_list = status.split(',')
        play_details = play_details.filter(play_status__in=status_list)

    if openrun == 'Y':
        play_details = play_details.filter(openrun='Y')

    if genre != '전체':
        play_details = play_details.filter(genre=genre)

    if keyword != '전체':
        play_details = play_details.filter(home_keyword__icontains=keyword)

    if gender != '전체':
        if gender == '남성':
            play_details = play_details.filter(male__gt=F('female'))
        elif gender == '여성':
            play_details = play_details.filter(female__gt=F('male'))

    # 나이대 필터링
    if age != '전체':
        play_details = play_details.annotate(
            teenage_float=Cast('teenage', FloatField()),
            twenty_float=Cast('twenty', FloatField()),
            thirty_float=Cast('thirty', FloatField()),
            forty_float=Cast('forty', FloatField()),
            fifty_float=Cast('fifty', FloatField())
        )
        # 각 연령대 필터 적용
        age_filter = {
            '10대': Q(teenage_float__gt=F('twenty_float')) & Q(teenage_float__gt=F('thirty_float')) & Q(
                teenage_float__gt=F('forty_float')) & Q(teenage_float__gt=F('fifty_float')),
            '20대': Q(twenty_float__gt=F('teenage_float')) & Q(twenty_float__gt=F('thirty_float')) & Q(
                twenty_float__gt=F('forty_float')) & Q(twenty_float__gt=F('fifty_float')),
            '30대': Q(thirty_float__gt=F('teenage_float')) & Q(thirty_float__gt=F('twenty_float')) & Q(
                thirty_float__gt=F('forty_float')) & Q(thirty_float__gt=F('fifty_float')),
            '40대': Q(forty_float__gt=F('teenage_float')) & Q(forty_float__gt=F('twenty_float')) & Q(
                forty_float__gt=F('thirty_float')) & Q(forty_float__gt=F('fifty_float')),
            '50대+': Q(fifty_float__gt=F('teenage_float')) & Q(fifty_float__gt=F('twenty_float')) & Q(
                fifty_float__gt=F('thirty_float')) & Q(fifty_float__gt=F('forty_float'))
        }
        if age in age_filter:
            play_details = play_details.filter(age_filter[age])

    play_details = play_details[:limit]  # 개수 제한

    # 쿼리셋을 리스트로 변환하기 전에 필요한 필드만 선택
    play_details_list = list(
        play_details.values('play_id', 'play_name', 'play_poster', 'play_strdate', 'play_enddate', 'play_status',
                            'theater_nm'))

    return JsonResponse({'play_details': play_details_list})

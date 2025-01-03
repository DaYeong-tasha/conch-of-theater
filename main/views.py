from django.shortcuts import render
from COT import settings
from common.models import Play_detail
from map.views import get_theaters_data
from django.http import JsonResponse
from django.db.models import F, FloatField, Q
from django.db.models.functions import Cast



def get_play_details():
    """공연중 또는 공연 예정인 Play_detail 데이터를 가져오기 (최적화)"""
    # 필드만 필요한 값들로 제한하고, 쿼리셋을 최적화
    return Play_detail.objects.filter(
        Q(play_status='공연중') | Q(play_status='공연예정')
    ).values(
        'play_id', 'play_name', 'play_poster',
        'play_strdate', 'play_enddate', 'play_status', 'theater_nm'
    )

def home(request):
    """홈 화면 최적화"""
    selected_area = request.GET.get('link_area', '전국')  # 기본값: '전국'
    selected_ststype = request.GET.get('ststypes', 'day')  # 기본값: 'day'

    # 공연중 또는 공연 예정인 Play_detail 데이터 가져오기
    play_details = get_play_details()

    # 극장 데이터 가져오기
    theater_context = get_theaters_data()

    # 극장 데이터 유효성 검증 및 추출
    theaters = theater_context.get('theaters', [])

    # context에 필요한 데이터만 포함시켜서 전달
    context = {
        'theaters': theaters,
        'kakao_map_api_key': settings.KAKAO_MAP_API_KEY,
        'play_details': play_details,  # 추가된 부분
    }

    # 로그인 여부에 따라 적절한 템플릿 렌더링
    template_name = 'main/home.html' if request.user.is_authenticated else 'main/before_login.html'
    return render(request, template_name, context)

import logging

logger = logging.getLogger(__name__)

# main/views.py

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
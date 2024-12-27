from django.shortcuts import render, get_object_or_404
from django.db.models import Max

from COT import settings
from common.models import Play_rank, Play_list, Play_detail
from map.views import get_theaters_data
from django.db.models import F, FloatField, Q
from django.db.models.functions import Cast
from django.http import JsonResponse
from common.models import Play_detail
from django.db.models import Q

def get_play_details():
    """공연중 또는 공연 예정인 Play_detail 데이터를 가져오기"""
    play_details = Play_detail.objects.filter(
        play_status__in=['공연중', '공연예정']
    ).values('play_id', 'play_name', 'play_poster', 'play_strdate', 'play_enddate', 'play_status', 'theater_nm')

    return play_details


def get_latest_ranked_data(selected_area='전국', selected_ststype='day'):
    """날짜 기준으로 최신 rank_reg_date 데이터를 가져오기"""
    latest_date = Play_rank.objects.aggregate(
        latest_date=Max('rank_reg_date')
    )['latest_date']

    if latest_date:
        # 최신 날짜 기준으로 필터링
        ranked_data = Play_rank.objects.filter(
            rank_reg_date__date=latest_date.date()
        ).order_by('rank')

        if selected_area:
            #print(f"Filter by link_area: {selected_area}")
            ranked_data = ranked_data.filter(link_area=selected_area)
        if selected_ststype:
            #print(f"Filter by ststypes: {selected_ststype}")
            ranked_data = ranked_data.filter(ststypes=selected_ststype)

        #print(f"DEBUG: Final QuerySet = {ranked_data}")
        return ranked_data

    return Play_rank.objects.none()


def get_ranked_context(selected_area='전국', selected_ststype='day'):
    """공통 데이터를 처리하고 context를 반환"""
    ranked_data = get_latest_ranked_data(selected_area, selected_ststype)
    link_area = ['전국', '서울', '경기', '충청', '경상', '전라', '강원', '대학로', '제주']
    ststypes = [
        {'key': 'day', 'label': '일별'},
        {'key': 'week', 'label': '주별'},
        {'key': 'month', 'label': '월별'}
    ]

    return {
        'ranked_data': ranked_data,
        'link_area': link_area,
        'ststypes': ststypes,
        'selected_area': selected_area,
        'selected_ststype': selected_ststype,
    }


def play_rank(request):
    """랭킹 페이지"""
    selected_area = request.GET.get('link_area', '전국')  # 기본값: '전국'
    selected_ststype = request.GET.get('ststypes', 'day')  # 기본값: 'day'

    #print(f"DEBUG - link_area: {selected_area}, ststypes: {selected_ststype}")

    context = get_ranked_context(selected_area, selected_ststype)
    return render(request, 'play_rank_base.html', context)



# 랭크를 대시보드로 옮겼으니, 수정하고,
# 엔간하면, 지도, 순위, 홈 다 분리할 것
def home(request):
    play_details = Play_detail.objects.all().order_by('-play_enddate')

    """홈 화면"""
    selected_area = request.GET.get('link_area', '전국')  # 기본값: '전국'
    selected_ststype = request.GET.get('ststypes', 'day')  # 기본값: 'day'

    #print(f"DEBUG - home - link_area: {selected_area}, ststypes: {selected_ststype}")
    # 기본 필터 조건으로 공통 데이터를 가져옴 #홈에 가지고 와야 띄우지? ^^
    context = get_ranked_context(selected_area, selected_ststype)

    # 공연중 또는 공연 예정인 Play_detail 데이터 가져오기
    # play_details = get_play_details()

    # 극장 데이터 가져오기
    theater_context = get_theaters_data()

    # 극장 데이터 유효성 검증
    theaters = theater_context.get('theaters', [])

    context.update({
        'theaters': theaters,
        'kakao_map_api_key': settings.KAKAO_MAP_API_KEY,
        'play_details': play_details,  # 추가된 부분
    })

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


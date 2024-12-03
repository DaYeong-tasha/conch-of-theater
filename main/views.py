from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Max

from COT import settings
from common.models import Play_rank, Play_list, Theater_location
from map.views import get_theaters_data
from django.utils import timezone


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


def toggle_favorite(request, play_id):
    """즐겨찾기 추가/제거"""
    if not request.user.is_authenticated:
        return JsonResponse({'message': '로그인 후 이용해주세요.'}, status=400)

    try:
        play_list = Play_list.objects.get(play_id=play_id)
    except Play_list.DoesNotExist:
        return JsonResponse({'message': '해당 연극이 존재하지 않습니다.'}, status=404)

    try:
        is_favorite = play_list.favorite_users.filter(id=request.user.id).exists()
        if is_favorite:
            play_list.favorite_users.remove(request.user)
            message = '즐겨찾기 해제되었습니다.'
        else:
            play_list.favorite_users.add(request.user)
            message = '즐겨찾기가 추가되었습니다.'
    except Exception as e:
        return JsonResponse({'message': f'오류 발생: {str(e)}'}, status=500)

    return JsonResponse({'message': message}, status=200)


def home(request):
    """홈 화면"""
    selected_area = request.GET.get('link_area', '전국')  # 기본값: '전국'
    selected_ststype = request.GET.get('ststypes', 'day')  # 기본값: 'day'

    #print(f"DEBUG - home - link_area: {selected_area}, ststypes: {selected_ststype}")
    # 기본 필터 조건으로 공통 데이터를 가져옴 #홈에 가지고 와야 띄우지? ^^
    context = get_ranked_context(selected_area, selected_ststype)

    # 극장 데이터 가져오기
    theater_context = get_theaters_data()

    # 극장 데이터 유효성 검증
    theaters = theater_context.get('theaters', [])

    context.update({
        'theaters': theaters,
        'kakao_map_api_key': settings.KAKAO_MAP_API_KEY,
    })

    template_name = 'main/home.html' if request.user.is_authenticated else 'main/before_login.html'
    return render(request, template_name, context)



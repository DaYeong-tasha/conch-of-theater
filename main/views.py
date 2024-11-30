from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Max
from common.models import Play_rank, Play_list
from django.utils import timezone


def get_latest_ranked_data(selected_area='서울', selected_ststype='day'):
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
            ranked_data = ranked_data.filter(link_area=selected_area)
        if selected_ststype:
            ranked_data = ranked_data.filter(ststypes=selected_ststype)

        return ranked_data

    return Play_rank.objects.none()


def get_ranked_context(selected_area='서울', selected_ststype='day'):
    """공통 데이터를 처리하고 context를 반환"""
    ranked_data = get_latest_ranked_data(selected_area, selected_ststype)
    link_area = Play_rank.objects.values('link_area').distinct()
    ststypes = Play_rank.objects.values('ststypes').distinct()

    return {
        'ranked_data': ranked_data,
        'link_area': link_area,
        'ststypes': ststypes,
        'selected_area': selected_area,
        'selected_ststype': selected_ststype,
    }


def play_rank(request):
    """랭킹 페이지"""
    selected_area = request.GET.get('link_area', '전체')  # 기본값: '서울'
    selected_ststype = request.GET.get('ststypes', 'day')  # 기본값: 'day'

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
    template_name = 'main/home.html' if request.user.is_authenticated else 'main/before_login.html'

    # 기본 필터 조건으로 공통 데이터를 가져옴
    context = get_ranked_context(selected_area='전체', selected_ststype='day')
    return render(request, template_name, context)

from django.shortcuts import render
from common.models import Play_rank
from django.db.models import Max


def get_latest_ranked_data(selected_area='전국', selected_ststype='day'):
    """날짜 기준으로 최신 rank_reg_date 데이터를 가져오기"""
    latest_date = Play_rank.objects.aggregate(
        latest_date=Max('rank_reg_date')
    )['latest_date']

    if latest_date:
        ranked_data = Play_rank.objects.filter(
            rank_reg_date__date=latest_date.date()
        ).order_by('rank')

        if selected_area:
            ranked_data = ranked_data.filter(link_area=selected_area)
        if selected_ststype:
            ranked_data = ranked_data.filter(ststypes=selected_ststype)

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

    context = get_ranked_context(selected_area, selected_ststype)
    return render(request, 'play_rank_base.html', context)


def dashboard(request):
    """대시보드 홈 화면"""
    selected_area = request.GET.get('link_area', '전국')  # 기본값: '전국'
    selected_ststype = request.GET.get('ststypes', 'day')  # 기본값: 'day'

    context = get_ranked_context(selected_area, selected_ststype)
    return render(request, 'dashboard/dashboard.html', context)

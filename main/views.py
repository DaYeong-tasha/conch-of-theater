import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from common.models import Play_rank, Play_list
import pytz
from django.db.models import Max


def home(request):
    # `rank_reg_date`가 가장 최신인 데이터의 `날짜`와 `시간` (초 제외) 가져오기
    kst = pytz.timezone('Asia/Seoul')
    latest_rank_date = (
        Play_rank.objects.annotate(latest_date=Max('rank_reg_date'))
        .values_list('latest_date', flat=True)
        .order_by('-latest_date')
        .first()
    )

    if latest_rank_date:
        # 초를 제외한 기준시간 계산
        latest_rank_date = latest_rank_date.astimezone(kst).replace(second=0, microsecond=0)

        # 최신 `rank_reg_date`와 일치하는 데이터만 필터링
        ranked_data = Play_rank.objects.filter(rank_reg_date__gte=latest_rank_date).order_by('rank')
    else:
        ranked_data = Play_rank.objects.none()

    if request.user.is_authenticated:  # 로그인 여부 체크
        # Play_list에서 해당 연극의 즐겨찾기 여부를 미리 가져오기
        play_ids = [play.play_id for play in ranked_data]
        play_lists = Play_list.objects.filter(play_id__in=play_ids)

        # 로그인한 사용자가 각 연극을 즐겨찾기 했는지 확인
        for play in ranked_data:
            play_list = play_lists.filter(play_id=play.play_id).first()
            play.is_favorite = play_list.favorite_users.filter(id=request.user.id).exists() if play_list else False

        return render(request, 'main/home.html', {'ranked_data': ranked_data})
    else:
        return render(request, 'main/before_login.html', {'ranked_data': ranked_data})

def toggle_favorite(request, play_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message': '로그인 후 이용해주세요.'}, status=400)

    try:
        play_list = Play_list.objects.get(play_id=play_id)
    except Play_list.DoesNotExist:
        return JsonResponse({'message': '해당 연극이 존재하지 않습니다.'}, status=404)

    is_favorite = request.user in play_list.favorite_users.all()

    try:
        if is_favorite:
            play_list.favorite_users.remove(request.user)
            message = '즐겨찾기 해제되었습니다.'
        else:
            play_list.favorite_users.add(request.user)
            message = '즐겨찾기가 추가되었습니다.'
    except Exception as e:
        return JsonResponse({'message': f'오류 발생: {str(e)}'}, status=500)

    return JsonResponse({'message': message}, status=200)

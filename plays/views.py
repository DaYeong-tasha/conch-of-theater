from django.shortcuts import render, get_object_or_404
from common.models import Play_detail, Review, Theater_location
from django.conf import settings

def play_detail(request, pk):
    play_detail = get_object_or_404(Play_detail, pk=pk)
    # mt10id 필드가 이미 Theater_location 객체를 반환하므로, 추가 조회가 필요없음
    theater_location = play_detail.mt10id  # 직접 ForeignKey 객체 사용
    # reviews = Review.objects.filter(play_id=pk)
    
    return render(request, 'plays/play_detail.html',
                {'play_detail': play_detail, 
                # 'reviews': reviews,
                'theater_location': theater_location,
                'KAKAO_MAP_API_KEY': settings.KAKAO_MAP_API_KEY})
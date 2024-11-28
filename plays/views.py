from django.shortcuts import render, get_object_or_404
from common.models import Play_detail, Review, Theater_location
from django.conf import settings

def play_detail(request, pk):
    play_detail = get_object_or_404(Play_detail, play_id=pk)
    reviews = Review.objects.filter(play_id=pk)
    theater = get_object_or_404(Theater_location, mt10id=play_detail.mt10id)
    
    context = {
        'play_detail': play_detail,
        'reviews': reviews,
        'theater': theater,
        'kakao_map_api_key': settings.KAKAO_MAP_API_KEY
    }
    return render(request, 'plays/play_detail.html', context)
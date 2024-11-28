from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from common.models import Play_detail, Review


def play_detail(request, pk):
    play_detail = get_object_or_404(Play_detail, pk=pk)
    reviews = Review.objects.filter(play_id=pk)
    return render(request, 'plays/play_detail.html',
                  {'play_detail': play_detail, 'reviews': reviews})
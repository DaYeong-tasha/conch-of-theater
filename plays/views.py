from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from common.models import Play_detail, Review, Theater_location
from django.conf import settings

def play_detail(request, pk):
    play_detail = get_object_or_404(Play_detail, pk=pk)
    # mt10id 필드가 이미 Theater_location 객체를 반환하므로, 추가 조회가 필요없음
    theater_location = play_detail.mt10id  # 직접 ForeignKey 객체 사용

    return render(request, 'plays/play_detail.html',
                {'play_detail': play_detail, 
                'theater_location': theater_location,
                'KAKAO_MAP_API_KEY': settings.KAKAO_MAP_API_KEY})


# 연극 상세 - 리뷰
def play_review(request):
    reviews = Review.objects.all()
    return render(request, 'plays/play_review.html', {'reviews': reviews})



@login_required
@require_POST
def toggle_like(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    user = request.user

    if user in review.like_users.all():
        review.like_users.remove(user)
    else:
        review.like_users.add(user)
        if user in review.dislike_users.all():
            review.dislike_users.remove(user)

    return JsonResponse({
        'like_count': review.like_users.count(),
        'dislike_count': review.dislike_users.count()
    })

@login_required
@require_POST
def toggle_dislike(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    user = request.user

    if user in review.dislike_users.all():
        review.dislike_users.remove(user)
    else:
        review.dislike_users.add(user)
        if user in review.like_users.all():
            review.like_users.remove(user)

    return JsonResponse({
        'like_count': review.like_users.count(),
        'dislike_count': review.dislike_users.count()
    })

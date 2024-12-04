from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from common.models import Play_detail, Review, Theater_location, Play_list
from django.conf import settings

from plays.forms import ReviewForm
from django.views.generic import ListView


def play_detail(request, pk):
    play_detail = get_object_or_404(Play_detail, pk=pk)
    play_list = get_object_or_404(Play_list, pk=pk)

    # mt10id 필드가 이미 Theater_location 객체를 반환하므로, 추가 조회가 필요없음
    theater_location = play_detail.mt10id  # 직접 ForeignKey 객체 사용

    return render(request, 'plays/play_detail.html',
                {'play_detail': play_detail,
                        'play_list': play_list,
                        'theater_location': theater_location,
                        'KAKAO_MAP_API_KEY': settings.KAKAO_MAP_API_KEY})



# 연극 상세 - 리뷰 ListView아닌 버전
# def play_review(request, play_id):
#     reviews = Review.objects.filter(play_id=play_id).order_by('-review_reg_date')
#     return render(request, 'plays/play_review.html',
#                   {'reviews': reviews, 'user': request.user, 'play_id': play_id})

# 연극 상세 - 리뷰
class PlayReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'plays/play_review.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        play_id = self.kwargs['play_id']
        queryset = Review.objects.filter(play_id=play_id)

        # 정렬 기능 추가
        sort = self.request.GET.get('sort', 'latest')
        if sort == 'likes':
            queryset = queryset.annotate(num_likes=Count('like_users')).order_by('-num_likes')
        elif sort == 'dislikes':
            queryset = queryset.annotate(num_dislikes=Count('dislike_users')).order_by('-num_dislikes')
        elif sort == 'oldest':
            queryset = queryset.order_by('review_reg_date')
        else:
            queryset = queryset.order_by('-review_reg_date')

        # 검색 기능 추가
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '')
        valid_search_types = ['all', 'play_name', 'theater_nm', 'loc', 'review_title', 'review_contents']
        if search_type not in valid_search_types:
            search_type = 'all'

        if search_keyword:
            if search_type == 'all':
                queryset = queryset.filter(
                    Q(review_title__icontains=search_keyword) |
                    Q(review_contents__icontains=search_keyword)
                )

            elif search_type == 'review_title':
                queryset = queryset.filter(review_title__icontains=search_keyword)
            elif search_type == 'review_contents':
                queryset = queryset.filter(review_contents__icontains=search_keyword)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['play_id'] = self.kwargs['play_id']
        return context




@require_POST
def toggle_like(request, review_id):
    if request.user.is_authenticated:
        review = Review.objects.get(pk=review_id)
        play_id = review.play_id.pk
        if review.username == request.user:
            messages.error(request, '작성자는 좋아요를 누를 수 없습니다.')
        else:
            if review.like_users.filter(pk=request.user.pk).exists():
                review.like_users.remove(request.user)
                messages.success(request, '좋아요 취소 완료!😢')
            else:
                review.like_users.add(request.user)
                messages.success(request, '좋아요 반영 완료!😄')
        return HttpResponseRedirect(reverse('plays:play_detail', args=[play_id]) + '?tab=review-info')
    return redirect('login')


@require_POST
def toggle_dislike(request, review_id):
    if request.user.is_authenticated:
        review = Review.objects.get(pk=review_id)
        play_id = review.play_id.pk
        if review.username == request.user:
            messages.error(request, '작성자는 싫어요를 누를 수 없습니다.')
        else:
            if review.dislike_users.filter(pk=request.user.pk).exists():
                review.dislike_users.remove(request.user)
                messages.success(request, '싫어요 취소 완료!😊')
            else:
                review.dislike_users.add(request.user)
                messages.success(request, '싫어요 반영 완료!😠')
        return HttpResponseRedirect(reverse('plays:play_detail', args=[play_id]) + '?tab=review-info')
    return redirect('login')


@require_POST
def toggle_play_favorite(request, play_id):
    if request.user.is_authenticated:
        play = get_object_or_404(Play_list, pk=play_id)
        if play.favorite_users.filter(pk=request.user.pk).exists():
            play.favorite_users.remove(request.user)
            messages.success(request, '즐겨찾기 취소 완료!')
        else:
            play.favorite_users.add(request.user)
            messages.success(request, '즐겨찾기 반영 완료!')


        return HttpResponseRedirect(reverse('plays:play_detail', args=[play_id]) + '?tab=play-info')
    return redirect('login')

@require_POST
def toggle_play_like(request, play_id):
    pass

@require_POST
def toggle_play_dislike(request, play_id):
    pass
# 찐
@login_required(login_url='login')
def write_review(request, play_id):
    play = get_object_or_404(Play_detail, pk=play_id)
    if request.method == 'GET':
        form = ReviewForm()
        return render(request, 'plays/play_review_write.html', {'form': form, 'play_id': play_id})

    elif request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.play_id = play
            review.theater_nm = play.theater_nm
            review.play_name = play.play_name
            review.loc = play.loc
            review.username = request.user
            review.save()
            messages.success(request, '리뷰가 작성되었습니다.')
            return redirect('plays:play_detail', pk=play_id)

    return render(request, 'plays/play_review_write.html', {'form': form, 'play_id': play_id})





@login_required(login_url='login')
def edit_review(request, play_id, review_id):
    play = get_object_or_404(Play_detail, pk=play_id)
    review = get_object_or_404(Review, pk=review_id)

    if review.username != request.user:
        messages.error(request, "수정 권한이 없습니다.")
        return redirect('plays:play_detail', pk=play_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "수정되었습니다.")
            return redirect('plays:play_detail', pk=play_id)  # 수정 후 리디렉션할 뷰 이름
    else:
        form = ReviewForm(instance=review)
    return render(request, 'plays/play_review_write.html', {'form': form, 'review': review, 'play_id': play_id, 'play':play})


@login_required
@require_POST
def delete_review(request, play_id, review_id):
    play = get_object_or_404(Play_detail, pk=play_id)
    review = get_object_or_404(Review, pk=review_id)

    if review.username == request.user:
        review.delete()
        messages.success(request, '리뷰가 삭제되었습니다.')

        return redirect('plays:play_detail', pk=play_id)

    else:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('plays:play_detail', pk=play_id)


# 커밋용 수정
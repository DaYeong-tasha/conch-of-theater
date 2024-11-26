from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from common.models import Review


# Create your views here.
class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    paginate_by = 10 # 한 페이지에 보여줄 게시글 수
    template_name = 'reviews/review_list.html'  # 사용할 템플릿
    context_object_name = 'reviews'  # 템플릿에서 사용할 컨텍스트 이름
    login_url = 'login'  # 로그인 페이지 url 설정

    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.request.GET.get('sort', 'latest')

        # 정렬 기능
        if sort == 'likes':
            queryset = queryset.annotate(num_likes=Count('like_users')).order_by('-num_likes')
        elif sort == 'dislikes':
            queryset = queryset.annotate(num_dislikes=Count('dislike_users')).order_by('-num_dislikes')
        elif sort == 'oldest':
            queryset = queryset.order_by('review_reg_date')
        else:
            queryset = queryset.order_by('-review_reg_date')

        # 검색 기능
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '')
        valid_search_types = ['all', 'play_name', 'theater_nm', 'loc', 'review_title', 'review_contents']
        if search_type not in valid_search_types:
            search_type = 'all'

        if search_keyword:
            # 전체 검색
            if search_type == 'all':
                queryset = queryset.filter(
                    Q(play_name__icontains=search_keyword) |
                    Q(theater_nm__icontains=search_keyword) |
                    Q(loc__icontains=search_keyword) |
                    Q(review_title__icontains=search_keyword) |
                    Q(review_contents__icontains=search_keyword)
                )
            # 연극명으로 검색
            elif search_type == 'play_name':
                queryset = queryset.filter(play_name__icontains=search_keyword)
            # 공연장명으로 검색
            elif search_type == 'theater_nm':
                queryset = queryset.filter(theater_nm__icontains=search_keyword)
            # 공연장 지역으로 검색
            elif search_type == 'loc':
                queryset = queryset.filter(loc__icontains=search_keyword)
            # 리뷰 제목으로 검색
            elif search_type == 'review_title':
                queryset = queryset.filter(review_title__icontains=search_keyword)
            # 리뷰 내용으로 검색
            elif search_type == 'review_contents':
                queryset = queryset.filter(review_contents__icontains=search_keyword)

        return queryset



# 리뷰 작성
@login_required(login_url='login')  # 로그인 필수 지정
def review_write(request):
    pass


# 리뷰 상세보기
# 연극제목 누르면 연극 상세페이지로 가도록 할 예정
@login_required(login_url='login')  # 로그인 필수 지정
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)

    context = {
        'review': review,
        }
    return render(request, 'reviews/review_detail.html', context)



# 리뷰 수정
@login_required(login_url='login')  # 로그인 필수 지정
def review_edit(request, pk):
    pass



# 리뷰 삭제
@login_required(login_url='login')  # 로그인 필수 지정
def review_delete(request, pk):
    review_one = get_object_or_404(Review, pk=pk)

    if review_one.username == request.user:
        review_one.delete()
        messages.success(request, '리뷰가 삭제되었습니다.')

        return redirect('review')  # 리뷰 목록으로 redirect

    else:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('/reviews/review/' + str(pk))  # 게시글 상세보기로 redirect



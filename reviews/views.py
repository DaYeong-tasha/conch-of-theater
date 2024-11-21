from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView


# Create your views here.
class ReviewListView(LoginRequiredMixin, ListView):
    template_name = 'review/review_list.html'  # 사용할 템플릿
    context_object_name = 'reviews'  # 템플릿에서 사용할 컨텍스트 이름

    def get_queryset(self):
        pass
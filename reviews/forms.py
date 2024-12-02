from django import forms
from django.forms import ModelForm
from common.models import Review

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['review_title', 'review_contents', 'star']

        widgets = {
            'review_title': forms.Textarea(attrs={
                'style': 'border: none; outline: none;',
                'placeholder': '제목을 입력하세요...',
            }),

            'review_contents': forms.Textarea(attrs={
                'style': 'border: none; outline: none;',
                'placeholder': '내용을 입력하세요...',
            }), }
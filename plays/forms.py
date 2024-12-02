from django import forms
from common.models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_title', 'review_contents', 'star']
        labels = {
            'review_title': '제목',
            'review_contents' : '내용',
            'star': '별점'
        }
        widgets = {
            'review_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '제목을 입력하세요..',
                'style': 'max-width: 800px; margin-top: 15px;'
            }),
            'review_contents': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '내용을 입력하세요..',
                'style': 'max-width: 800px; height: 200px; margin-top: 15px;'
            }),
            'star': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 400px; margin-top: 15px;'
            }),
        }


from django import forms
from django.contrib.auth.models import AbstractUser
from django.forms import ModelForm

from common.models import Review
from accounts.models import Users 

#장고 password랑 부딪히지 x, 제약조건 수월하게 걸기 위함.
class LoginForm(forms.Form):
    username = forms.CharField(max_length=65) # 유저 아이디
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


#회원정보 수정
# 성별 선택 옵션
GENDER_CHOICES = [
    ('남성', '남성'),
    ('여성', '여성'),
    ('기타', '기타'),
]

# 지역 선택 옵션
ADDRESS_CHOICES = [
    ('서울특별시', '서울특별시'),
    ('부산광역시', '부산광역시'),
    ('대구광역시', '대구광역시'),
    ('인천광역시', '인천광역시'),
    ('광주광역시', '광주광역시'),
    ('대전광역시', '대전광역시'),
    ('울산광역시', '울산광역시'),
    ('세종특별자치시', '세종특별자치시'),
    ('경기도', '경기도'),
    ('강원도', '강원도'),
    ('충청북도', '충청북도'),
    ('충청남도', '충청남도'),
    ('전라북도', '전라북도'),
    ('전라남도', '전라남도'),
    ('경상북도', '경상북도'),
    ('경상남도', '경상남도'),
    ('제주특별자치도', '제주특별자치도'),
]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['fullname', 'email', 'birth', 'gender', 'address', 'my_genre', 'my_actor']
        widgets = {
            'birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=GENDER_CHOICES),  # 성별 선택 드롭다운
            'address': forms.Select(choices=ADDRESS_CHOICES),  # 지역 선택 드롭다운
            'my_actor': forms.TextInput(attrs={'placeholder': '배우를 입력하세요'}),
            'my_genre': forms.TextInput(attrs={'type': 'hidden', 'id': 'my_genre_input'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['my_actor'].required = False
        self.fields['my_genre'].required = False


        # 선택적 검증 예시 (커스텀 검증 추가 가능)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("이메일을 입력해주세요.")
        return email




class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['review_title', 'review_contents', 'star']
        labels = {
            'review_title': '제목',
            'review_contents': '내용',
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
from django import forms

from accounts.models import Users


#장고 password랑 부딪히지 x, 제약조건 수월하게 걸기 위함.
class LoginForm(forms.Form):
    username = forms.CharField(max_length=65) # 유저 아이디
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


#회원정보 수정

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['fullname', 'email', 'birth', 'gender', 'my_keyword', 'my_act', 'address', 'preferences']
        widgets = {
            'address': forms.TextInput(attrs={'readonly': 'readonly'}),
            'preferences': forms.Textarea(attrs={'readonly': 'readonly'}),
            'birth': forms.DateInput(attrs={'type': 'date'}),  # 날짜 입력 개선
        }



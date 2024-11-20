from django import forms

#장고 password랑 부딪히지 x, 제약조건 수월하게 걸기 위함.
class LoginForm(forms.Form):
    username = forms.CharField(max_length=65) # 유저 아이디
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)
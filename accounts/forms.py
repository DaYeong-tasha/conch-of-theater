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
        fields = ['fullname', 'email', 'birth', 'gender', 'my_actor', 'my_play_keyword', 'my_play_mood', 'address', 'my_genre']
        widgets = {
            'address': forms.TextInput(attrs={'readonly': 'readonly'}),
            'my_genre': forms.Textarea(attrs={'readonly': 'readonly'}),
            'my_mood': forms.Textarea(attrs={'readonly': 'readonly'}),
            'birth': forms.DateInput(attrs={'type': 'date'}),  # 날짜 입력 개선
        }

        # 필드를 수정할 수 없도록 clean() 메서드 오버라이드
        def clean(self):
            cleaned_data = super().clean()
            # 읽기 전용 필드의 값 강제 유지
            if 'address' in cleaned_data:
                cleaned_data['address'] = self.instance.address
            if 'my_play_keyword' in cleaned_data:
                cleaned_data['my_play_keyword'] = self.instance.my_play_keyword
            if 'my_play_mood' in cleaned_data:
                cleaned_data['my_play_mood'] = self.instance.my_play_mood
            return cleaned_data

    '''
        def clean_address(self):
            return self.instance.address  # 변경하지 않도록 반환

        def clean_my_genre(self):
            return self.instance.my_genre  # 변경하지 않도록 반환

        def clean_my_mood(self):
            return self.instance.my_mood  # 변경하지 않도록 반환
    '''




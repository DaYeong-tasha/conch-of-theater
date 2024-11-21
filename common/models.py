from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Users(AbstractUser):
    # 전체적으로 blank=False 추가(username 제외)
    username = models.CharField(primary_key=True, max_length=150, blank=False)
    #password = models.CharField(max_length=150,  blank=False) #장고가 알아서함
    fullname = models.CharField(max_length=150, blank=False)
    address = models.CharField(max_length=150 , blank=False)
    birth = models.DateField(blank=False) # 유저가 계속 쓴다고 생각하면, 넣고 연령대 계산을 하는 것이 더 나아보임.
    # default='기타' 추가(MySQL에서 못불러옴)
    gender = models.CharField(max_length=10,default='기타',blank=False)
    # blank=False로 주기 위함 / MySQL에는 EmailField 타입이 없어 django에서 추가
    # django에서 자동으로 주니까 빼기
    email = models.EmailField(blank=False)

    # 선호 정보 json으로 받아야 추후 처리가 유용
    my_genre = models.JSONField(default=list, blank=False)  # 빈 리스트로 기본값 설정
    my_play_mood = models.JSONField(default=list, blank=False)  # 빈 리스트로 기본값 설정
    my_play_keyword = models.JSONField(default=list, blank=False)  # 빈 리스트로 기본값 설정
    my_actor = models.CharField(max_length=20, default="없음", blank=False)  # 기본값 "없음"

    class Meta:
        # managed = False #포함X, 커스텀 필드들이 db에 반영되지 않는 문제 방지
        db_table = 'users'

    def __str__(self):
        return self.username

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from django.conf import settings
from accounts.models import Users


### 외래키는 전부 on_delete=models.CASCADE로 설정


# Play_list : 연극 목록 모델 (common 앱에 위치)
class Play_list(models.Model):
    play_id = models.CharField(primary_key=True, max_length=50, blank=False)
    play_name = models.CharField(max_length=300, blank=False)
    play_reg_date = models.DateTimeField() # API에서 연극 리스트 불러온 날짜(DAG 트리거 날짜)
    genre = models.CharField(max_length=300, blank=False) # 우리가 구분해서 추가할 장르

    class Meta:
        # managed = False
        db_table = 'Play_list'

# Theater_location : 공연장 주소 모델 (common 앱에 위치)
class Theater_location(models.Model):
    mt10id = models.CharField(primary_key=True, max_length=50) # 공연시설ID
    theater_nm = models.CharField(max_length=300, blank=False) # 공연장명
    addr = models.CharField(max_length=300, blank=False) # 공연장 전체 주소
    # play_id = models.ForeignKey(Play_list, on_delete=models.CASCADE, db_column='play_id', blank=False)

    class Meta:
        # managed = False
        db_table = 'Theater_location'

# play_detail : 연극 상세 모델 (common 앱에 위치)
class Play_detail(models.Model):
    play_id = models.ForeignKey(Play_list, max_length=50, on_delete=models.CASCADE, db_column='play_id', blank=False)
    play_name = models.CharField(max_length=300, blank=False)
    genre = models.CharField(max_length=300, blank=False) # 우리가 구분해서 추가할 장르
    play_strdate = models.CharField(max_length=300, blank=False) # 시작일
    play_enddate = models.CharField(max_length=300, blank=False) # 종료일
    theater_nm = models.CharField(max_length=300, blank=False)  # 공연장명
    play_forcast = models.CharField(max_length=300, blank=False) # 출연진
    play_runtime = models.CharField(max_length=50, blank=False)  # 공연시간
    play_age = models.CharField(max_length=50, blank=False) # 관람 연령
    play_guidance = models.CharField(max_length=300, blank=False) # 가격 안내
    play_poster = models.CharField(max_length=300, blank=False) # 포스터 이미지 URL
    loc = models.CharField(max_length=300, blank=False) # 공연장 위치 중 지역만(ex. 서울특별시)
    play_status = models.CharField(max_length=50, blank=False) # 공연 상태
    styurls_1 = models.CharField(max_length=300, blank=False) # 상세이미지
    styurls_2 = models.CharField(max_length=300, blank=False)
    styurls_3 = models.CharField(max_length=300, blank=False)
    styurls_4 = models.CharField(max_length=300, blank=False)
    mt10id = models.ForeignKey(Theater_location, max_length=50, on_delete=models.CASCADE, db_column='mt10id', blank=False) # 공연시설ID
    dtguidance = models.CharField(max_length=300, blank=False) # 공연 시간 안내(ex.요일별 시간)
    relate_1 = models.CharField(max_length=300, blank=False) # 예매처이름
    relateurl_1 = models.CharField(max_length=300, blank=False) # 예매처url
    relate_2 = models.CharField(max_length=300, blank=False)
    relateurl_2 = models.CharField(max_length=300, blank=False)
    relate_3 = models.CharField(max_length=300, blank=False)
    relateurl_3 = models.CharField(max_length=300, blank=False)
    relate_4 = models.CharField(max_length=300, blank=False)
    relateurl_4 = models.CharField(max_length=300, blank=False)
    relate_5 = models.CharField(max_length=300, blank=False)
    relateurl_5 = models.CharField(max_length=300, blank=False)
    relate_6 = models.CharField(max_length=300, blank=False)
    relateurl_6 = models.CharField(max_length=300, blank=False)
    relate_7 = models.CharField(max_length=300, blank=False)
    relateurl_7 = models.CharField(max_length=300, blank=False)
    relate_8 = models.CharField(max_length=300, blank=False)
    relateurl_8 = models.CharField(max_length=300, blank=False)

    class Meta:
        # managed = False
        db_table = 'Play_detail'
        # 복합키(play_id가 외래키여서 기본키로 지정하지 않는 걸 권장함)
        constraints = [
            models.UniqueConstraint(fields=['play_id', 'play_name'], name='unique_Play_detail')
        ]





# Location : 지역명 모델 (common 앱에 위치)
class Location(models.Model):
    loc = models.CharField(primary_key=True, max_length=50, blank=False) # 지역명(ex. 서울특별시)

    class Meta:
        # managed = False
        db_table = 'Location'



# Play_rank : 연극 순위 모델 (common 앱에 위치)
# class Play_rank(models.Model):
#     rank_id = models.AutoField(primary_key=True) # PK용 필드
#     rank = models.IntegerField(blank=False) # 순위
#     play_id = models.CharField(max_length=300, blank=False)
#     play_name = models.CharField(max_length=300, blank=False)
#     play_period = models.CharField(max_length=300, blank=False) # 공연기간
#     theater_nm = models.CharField(max_length=300, blank=False)  # 공연장명
#     rank_area = models.CharField(max_length=50, blank=False) # 지역 (ex. 서울)
#     play_poster = models.CharField(max_length=300, blank=False)
#     ststypes = models.CharField(max_length=50, blank=False) # day/week/month
#     link_area = models.CharField(max_length=50, blank=False) # csv 저장용
#     rank_reg_date = models.DateTimeField() # API에서 연극 순위 불러온 날짜(DAG 트리거 날짜)
#
#     class Meta:
#         # managed = False
#         db_table = 'Play_rank'



# Review: 리뷰 모델 (common 앱에 위치)
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    play_id = models.ForeignKey(Play_detail, max_length=50, on_delete=models.CASCADE, db_column='play_id', blank=False)
    play_name = models.CharField(max_length=300, blank=False) # 리뷰 저장시 play_id를 통해 받아옴
    theater_nm = models.CharField(max_length=300, blank=False) # 리뷰 저장시 play_id를 통해 받아옴
    loc = models.CharField(max_length=300, blank=False) # 리뷰 저장시 play_id를 통해 받아옴(ex. 서울특별시)
    review_title = models.CharField(max_length=255, blank=False)
    review_contents = models.CharField(max_length=1000, blank=False)
    star = models.ForeignKey('Star', on_delete=models.CASCADE, db_column='star')

    # 오류나면 blank=True로 변경 예정
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='username', blank=False)
    review_reg_date = models.DateTimeField(auto_now_add=True, blank=True) # 리뷰 작성 날짜(자동)

    class Meta:
        # managed = False
        db_table = 'Review'



# Star: 별점 모델 (common 앱에 위치)
class Star(models.Model):
    star_total = models.DecimalField(primary_key=True, max_digits=2, decimal_places=1)

    class Meta:
        # managed = False
        db_table = 'Star'

    def __str__(self):
        # 숫자 -> 문자열 변환
        return str(self.star_total)



# Favorites : 즐겨찾기 모델 (common 앱에 위치)
class Favorites(models.Model):
    play_id = models.CharField(primary_key=True, max_length=50, blank=False)
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='username', blank=False)
    play_name = models.CharField(max_length=300, blank=False)

    class Meta:
        # managed = False
        db_table = 'Favorites'
        # 복합키(play_id나 username으로만 지정하면 중복되는 값이 있을 수 있어 기본키 불가능)
        constraints = [
            models.UniqueConstraint(fields=['play_id', 'username'], name='unique_favorite')
        ]
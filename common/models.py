from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings 


### 외래키는 전부 on_delete=models.CASCADE로 설정


# Play_list : 연극 목록 모델 (common 앱에 위치)
class Play_list(models.Model):
    play_id = models.CharField(primary_key=True, max_length=100)
    play_name = models.CharField(max_length=300)
    play_reg_date = models.DateTimeField() # API에서 연극 리스트 불러온 날짜(DAG 트리거 날짜)
    genre = models.CharField(max_length=300, blank=True, null=True) # 우리가 구분해서 추가할 장르

    # 좋아요
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_plays',
        blank=True
    )
    # 싫어요
    dislike_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='disliked_plays',
        blank=True
    )

    # 즐겨찾기
    favorite_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorited_plays',
        blank=True
    )

    class Meta:
        # managed = False
        db_table = 'Play_list'

    def __str__(self):
        return self.play_id

# Theater_location : 공연장 주소 모델 (common 앱에 위치)
# class Theater_location(models.Model):
#     mt10id = models.CharField(primary_key=True, max_length=50) # 공연시설ID
#     theater_nm = models.CharField(max_length=300) # 공연장명
#     theater_addr = models.CharField(max_length=300, db_column='theater_addr') # 공연장 전체 주소
#
#     class Meta:
#         # managed = False
#         db_table = 'Theater_location'



# play_detail : 연극 상세 모델 (common 앱에 위치)
class Play_detail(models.Model):
    play_id = models.OneToOneField(Play_list, on_delete=models.CASCADE, db_column='play_id', primary_key=True)
    play_name = models.CharField(max_length=300)
    genre = models.CharField(max_length=300, blank=True, null=True) # 우리가 구분해서 추가할 장르
    play_strdate = models.CharField(max_length=300) # 시작일
    play_enddate = models.CharField(max_length=300) # 종료일
    theater_nm = models.CharField(max_length=300)  # 공연장명
    play_forcast = models.CharField(max_length=300, null=True) # 출연진
    play_runtime = models.CharField(max_length=50, null=True)  # 공연시간
    play_age = models.CharField(max_length=50, null=True) # 관람 연령
    play_guidance = models.CharField(max_length=300, null=True) # 가격 안내
    play_poster = models.CharField(max_length=300, null=True) # 포스터 이미지 URL
    loc = models.CharField(max_length=300) # 공연장 위치 중 지역만(ex. 서울특별시)
    play_status = models.CharField(max_length=50) # 공연 상태
    styurls_1 = models.CharField(max_length=300, blank=True, null=True) # 상세이미지
    styurls_2 = models.CharField(max_length=300, blank=True, null=True)
    styurls_3 = models.CharField(max_length=300, blank=True, null=True)
    styurls_4 = models.CharField(max_length=300, blank=True, null=True)
    # mt10id = models.ForeignKey(Theater_location, on_delete=models.CASCADE, db_column='mt10id') # 공연시설ID
    dtguidance = models.CharField(max_length=500, blank=True, null=True) # 공연 시간 안내(ex.요일별 시간)
    child = models.CharField(max_length=10, blank=True, null=True)
    relate_1 = models.CharField(max_length=300, blank=True, null=True) # 예매처이름
    relateurl_1 = models.CharField(max_length=300, blank=True, null=True) # 예매처url
    relate_2 = models.CharField(max_length=300, blank=True, null=True)
    relateurl_2 = models.CharField(max_length=300, blank=True, null=True)
    relate_3 = models.CharField(max_length=300, blank=True, null=True)
    relateurl_3 = models.CharField(max_length=300, blank=True, null=True)
    relate_4 = models.CharField(max_length=300, blank=True, null=True)
    relateurl_4 = models.CharField(max_length=300, blank=True, null=True)
    relate_5 = models.CharField(max_length=300, blank=True, null=True)
    relateurl_5 = models.CharField(max_length=300, blank=True, null=True)
    relate_6 = models.CharField(max_length=300, blank=True, null=True)
    relateurl_6 = models.CharField(max_length=300, blank=True, null=True)
    relate_7 = models.CharField(max_length=300, blank=True, null=True)
    relateurl_7 = models.CharField(max_length=300, blank=True, null=True)
    relate_8 = models.CharField(max_length=300, blank=True, null=True)
    relateurl_8 = models.CharField(max_length=300, blank=True, null=True)
    male = models.CharField(max_length=10, null=True)
    female = models.CharField(max_length=10, null=True)
    teenage = models.CharField(max_length=10, null=True)
    twenty = models.CharField(max_length=10, null=True)
    thirty = models.CharField(max_length=10, null=True)
    forty = models.CharField(max_length=10, null=True)
    fifty = models.CharField(max_length=10, null=True)
    keyword = models.TextField(null=True)  # TextField로 리스트 형식을 문자열로 저장
    home_keyword = models.TextField(null=True)  # TextField로 리스트 형식을 문자열로 저장

    class Meta:
        # managed = False
        db_table = 'Play_detail'



# Location : 지역명 모델 (common 앱에 위치)
# class Location(models.Model):
#     loc = models.CharField(primary_key=True, max_length=50) # 지역명(ex. 서울특별시)
#
#     class Meta:
#         # managed = False
#         db_table = 'Location'



#Play_rank : 연극 순위 모델 (common 앱에 위치)
class Play_rank(models.Model):
    rank_id = models.AutoField(primary_key=True) # PK용 필드
    rank = models.IntegerField() # 순위
    play_id = models.CharField(max_length=300)
    play_name = models.CharField(max_length=300)
    play_period = models.CharField(max_length=300) # 공연기간
    theater_nm = models.CharField(max_length=300)  # 공연장명
    rank_area = models.CharField(max_length=50) # 지역 (ex. 서울)
    play_poster = models.CharField(max_length=300)
    ststypes = models.CharField(max_length=50) # day/week/month
    link_area = models.CharField(max_length=50) # csv 저장용
    rank_reg_date = models.DateTimeField() # API에서 연극 순위 불러온 날짜(DAG 트리거 날짜)

    class Meta:
        # managed = False
        db_table = 'Play_rank'

# Review: 리뷰 모델 (common 앱에 위치)
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    play_id = models.ForeignKey(Play_detail, on_delete=models.CASCADE, db_column='play_id')
    play_name = models.CharField(max_length=300) # 리뷰 저장시 play_id를 통해 받아옴
    theater_nm = models.CharField(max_length=300) # 리뷰 저장시 play_id를 통해 받아옴
    loc = models.CharField(max_length=300) # 리뷰 저장시 play_id를 통해 받아옴(ex. 서울특별시)
    review_title = models.CharField(max_length=255)
    review_contents = models.CharField(max_length=1000)
    star = models.ForeignKey('Star', on_delete=models.CASCADE, db_column='star')

    # 오류나면 blank=True로 변경 예정
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='username')
    review_reg_date = models.DateTimeField(auto_now_add=True, blank=True) # 리뷰 작성 날짜(자동)

    # 좋아요
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_reviews',
        blank=True
    )
    # 싫어요
    dislike_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='disliked_reviews',
        blank=True
    )

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

# commit용 수정사항

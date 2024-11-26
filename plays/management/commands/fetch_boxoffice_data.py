import requests
import xmltodict
from collections import defaultdict
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from common.models import Play_rank  # Django 모델 임포트
import time
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# crontab -e # 크론 열기 / vim임
# crontab -l #등록된 작업 확인

# KOPIS API 키 가져오기
service_key = os.getenv("KOPIS_API_KEY")

# 박스오피스 데이터 수집 기간 타입 (일간/주간/월간)
ststypes = ["day", "week", "month"]

# 지역별 코드 매핑 정보 수정 (순서 변경)
region_groups = {
    "전체": ["11", "41", "28", "43", "44", "30", "47", "48", "27", "26", "31", "45", "46", "29", "51", "50", "UNI"],
    "서울": ["11"],
    "경기": ["41", "28"],  # 41: 경기도, 28: 인천
    "충청": ["43", "44", "30"],  # 43: 충북, 44: 충남, 30: 대전
    "경상": ["47", "48", "27", "26", "31"],  # 47: 경북, 48: 경남, 27: 대구, 26: 울산, 31: 부산
    "전라": ["45", "46", "29"],  # 45: 전북, 46: 전남, 29: 광주
    "강원": ["51"],
    "제주": ["50"],
    "대학로": ["UNI"]
}

# 어제 날짜 계산 (현재 날짜 - 1일)
yesterday = datetime.now() - timedelta(days=1) # system 날짜라서.. 바로 전 날이 안돼. 이거 수정할 것.
date = yesterday.strftime("%Y%m%d")  # YYYYMMDD 형식으로 변환
print(f"데이터 수집 기준 날짜: {date}")

# CSV 파일에 저장될 컬럼명 정의 (DB 명세서 기준)
fieldnames = [
    "rank_id",  # 값 아이디
    "rank",  # 순위
    "play_id",  # 공연 ID
    "play_name",  # 공연명
    "play_period",  # 공연기간
    "theater_nm",  # 공연장명
    "rank_area",  # 지역
    "play_poster",  # 포스터이미지
    "ststypes",  # 일/주/월
    "link_area",  # csv저장용
    "rank_reg_date"  # 데이터 수집 날짜
]

# API 호출하여 데이터를 가져오는 함수 (재시도 로직 추가)
def fetch_boxoffice_data(ststype, area_code, date, retries=3, delay=2):
    url = f"https://kopis.or.kr/openApi/restful/boxoffice?service={service_key}&ststype={ststype}&date={date}&catecode=AAAA&area={area_code}"
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                print(f"API 요청 실패: {response.status_code} (ststype={ststype}, area={area_code})")
        except requests.RequestException as e:
            print(f"API 호출 중 예외 발생: {e} (ststype={ststype}, area={area_code})")
        time.sleep(delay)  # 재시도 전에 대기
    return None  # 여러 번 재시도 실패 시 None을 반환



# 지역별 데이터를 수집하고 순위를 매기는 함수
def aggregate_and_rank_by_region(ststype):
    region_ranked_data = []  # 전체 지역의 순위 데이터를 저장할 리스트

    # 각 지역별로 데이터 수집
    for region, area_codes in region_groups.items():
        region_aggregate_data = defaultdict(int)  # 공연별 관객 수 합산용 딕셔너리
        performance_info = {}  # 공연 정보 저장용 딕셔너리

        # 각 지역 코드별로 데이터 수집
        for area_code in area_codes:
            boxoffice_data = fetch_boxoffice_data(ststype, area_code, date)

            if boxoffice_data:
                try:
                    # XML 데이터 파싱
                    xml_data = xmltodict.parse(boxoffice_data)
                    boxofs = xml_data.get("boxofs", {}).get("boxof", [])

                    # 박스오피스 데이터가 리스트 형태인 경우 처리
                    if isinstance(boxofs, list):
                        for record in boxofs:
                            perf_id = record.get("mt20id", "")
                            audience_count = int(record.get("prfdtcnt", 0))
                            region_aggregate_data[perf_id] += audience_count  # 관객 수 합산

                            # 공연 정보 저장
                            if perf_id not in performance_info:
                                performance_info[perf_id] = {
                                    "perf_name": record.get("prfnm", ""),
                                    "performance_location": record.get("prfplcnm", ""),
                                    "performance_period": record.get("prfpd", ""),
                                    "poster": f"https://www.kopis.or.kr{record.get('poster', '')}"
                                }
                except Exception as e:
                    print(f"XML 파싱 오류 (ststype={ststype}, area={area_code}): {e}")
                    continue

        # 관객 수 기준으로 상위 50개 공연 정렬
        sorted_region_performances = sorted(region_aggregate_data.items(), key=lambda x: x[1], reverse=True)[:50]

        # 순위 데이터 생성
        for rank, (perf_id, total_audience) in enumerate(sorted_region_performances, start=1):
            performance = performance_info[perf_id]
            rank_reg_date = timezone.now()  # 현재 시간 저장
            region_ranked_data.append({
                #"rank_id": f"{ststype}_{region}_{rank}",  # 자동으로 생성
                "rank": rank,
                "play_id": perf_id,
                "play_name": performance["perf_name"],
                "play_period": performance["performance_period"],
                "theater_nm": performance["performance_location"],
                "rank_area": region,
                "play_poster": performance["poster"],
                "ststypes": ststype,
                "link_area": region,
                "rank_reg_date": rank_reg_date  # 현재 시간 추가
            })

    return region_ranked_data


# 수집된 데이터를 Django 모델에 저장하는 함수
def save_to_db(all_data):
    try:
        for data in all_data:
            Play_rank.objects.update_or_create(
                rank_id=data.get("rank_id"),  # rank_id를 명시적으로 넣지 않도록 수정
                defaults={
                    "rank": data["rank"],
                    "play_id": data["play_id"],
                    "play_name": data["play_name"],
                    "play_period": data["play_period"],
                    "theater_nm": data["theater_nm"],
                    "rank_area": data["rank_area"],
                    "play_poster": data["play_poster"],
                    "ststypes": data["ststypes"],
                    "link_area": data["link_area"],
                    "rank_reg_date": data["rank_reg_date"]
                }
            )
        print(f"모든 데이터를 DB에 저장했습니다.")
    except Exception as e:
        print(f"DB 저장 중 오류 발생: {str(e)}")


# Django 커맨드 클래스
def fetch_and_save_all_data():
    all_ranked_data = []

    # 일간, 주간, 월간 데이터를 각각 처리
    for ststype in ststypes:
        ranked_data = aggregate_and_rank_by_region(ststype)
        all_ranked_data.extend(ranked_data)

    # DB에 저장
    save_to_db(all_ranked_data)


class Command(BaseCommand):
    help = "KOPIS 박스오피스 데이터를 매일 크롤링하여 DB에 저장하는 커맨드"

    def handle(self, *args, **kwargs):
        # 메인 함수 실행
        fetch_and_save_all_data()
        self.stdout.write(self.style.SUCCESS('데이터를 성공적으로 수집하고 저장했습니다.'))

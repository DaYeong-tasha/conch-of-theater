import requests
import xmltodict
from collections import defaultdict
from datetime import datetime, timedelta
import pytz #한국 시간대
from django.core.management.base import BaseCommand
from django.utils import timezone

from common.models import Play_rank  # Django 모델 임포트
import time
import os
from dotenv import load_dotenv
from django.db import connection


# .env 파일 로드
load_dotenv()

# KOPIS API 키 가져오기
service_key = os.getenv("KOPIS_API_KEY")

# 박스오피스 데이터 수집 기간 타입 (일간/주간/월간)
ststypes = ["day", "week", "month"]

# 지역 코드와 지역명 매핑
area_code_to_region = {
    "11": "서울",
    "41": "경기",
    "28": "인천",
    "43": "충북",
    "44": "충남",
    "30": "대전",
    "47": "경북",
    "48": "경남",
    "27": "대구",
    "26": "울산",
    "31": "부산",
    "45": "전북",
    "46": "전남",
    "29": "광주",
    "51": "강원",
    "50": "제주",
    "UNI": "대학로"
}

# 지역별 코드 매핑 정보
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

# 한국 시간대 설정
kst = pytz.timezone('Asia/Seoul')

# 어제 날짜 계산 (현재 날짜 - 1일) 및 한국 시간으로 변환
yesterday = datetime.now(kst) - timedelta(days=1)
date = yesterday.strftime("%Y%m%d")  # YYYYMMDD 형식으로 변환
print(f"데이터 수집 기준 날짜: {date}")

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
def aggregate_and_rank_by_region(ststype, date):
    region_ranked_data = []  # 전체 지역의 순위 데이터를 저장할 리스트

    # 각 지역별로 데이터 수집
    for region, area_codes in region_groups.items():
        region_aggregate_data = defaultdict(int)  # 공연별 관객 수 합산용 딕셔너리
        performance_info = {}  # 공연 정보 저장용 딕셔너리

        # 각 지역 코드별로 데이터 수집
        for area_code in area_codes:
            boxoffice_data = fetch_boxoffice_data(ststype, area_code, date)  # date 전달

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
            # 날짜와 시간을 한국 기준
            rank_reg_date = datetime.now(kst)
            region_name = area_code_to_region.get(area_codes[0], "Unknown")  # 첫 번째 지역 코드에 해당하는 지역명만 가져옴
            region_ranked_data.append({
                "rank": rank,
                "play_id": perf_id,
                "play_name": performance["perf_name"],
                "play_period": performance["performance_period"],
                "theater_nm": performance["performance_location"],
                "rank_area": region_name,  # 첫 번째 지역 코드에 해당하는 지역명만 사용
                "play_poster": performance["poster"],
                "ststypes": ststype,
                "link_area": region,
                "rank_reg_date": rank_reg_date  # 데이터 수집 기준 날짜
            })

    return region_ranked_data

# 수집된 데이터를 Django 모델에 저장하는 함수
def save_to_db(all_data):
    try:
        for data in all_data:
            Play_rank.objects.update_or_create(
                play_id=data.get("play_id"),
                rank_reg_date=data.get("rank_reg_date"),  # 날짜 조건 추가
                defaults={
                    "rank": data["rank"],
                    "play_name": data["play_name"],
                    "play_period": data["play_period"],
                    "theater_nm": data["theater_nm"],
                    "rank_area": data["rank_area"],  # area_code 값 사용
                    "play_poster": data["play_poster"],
                    "ststypes": data["ststypes"],
                    "link_area": data["link_area"]
                }
            )
        print("모든 데이터를 DB에 저장했습니다.")
    except Exception as e:
        print(f"DB 저장 중 오류 발생: {str(e)}")



# 전체 데이터를 수집 및 저장하는 함수
def fetch_and_save_all_data():
    all_ranked_data = []

    # 일간, 주간, 월간 데이터를 각각 처리
    for ststype in ststypes:
        ranked_data = aggregate_and_rank_by_region(ststype, date)  # date 전달
        all_ranked_data.extend(ranked_data)

    # DB에 저장
    save_to_db(all_ranked_data)
    #rint(connection.queries)


# Django 커맨드 클래스
class Command(BaseCommand):
    help = "KOPIS 박스오피스 데이터를 매일 크롤링하여 DB에 저장하는 커맨드"

    def handle(self, *args, **kwargs):
        fetch_and_save_all_data()
        self.stdout.write(self.style.SUCCESS('데이터를 성공적으로 수집하고 저장했습니다.'))

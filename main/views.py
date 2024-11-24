import requests
from datetime import datetime, timedelta
from collections import defaultdict
from django.shortcuts import render
import xmltodict  # XML 파싱을 위한 라이브러리 추가

# KOPIS API 인증키
service_key = "69d72dcef51346ba8fbc7b4acec944df"

# 지역별 코드 매핑
region_groups = {
    "전체": ["11", "41", "28", "43", "44", "30", "47", "48", "27", "26", "31", "45", "46", "29", "51", "50", "UNI"],
    "서울": ["11"],
    "경기": ["41", "28"],
    "충청": ["43", "44", "30"],
    "경상": ["47", "48", "27", "26", "31"],
    "전라": ["45", "46", "29"],
    "강원": ["51"],
    "제주": ["50"],
    "대학로": ["UNI"]
}

# 어제 날짜 계산 (현재 날짜 - 1일)
yesterday = datetime.now() - timedelta(days=1)
date = yesterday.strftime("%Y%m%d")  # YYYYMMDD 형식으로 변환
print(f"데이터 수집 기준 날짜: {date}")


# API 호출하여 데이터를 가져오는 함수
def fetch_boxoffice_data(ststype, area_code, yesterday):
    # API URL 생성
    url = f"https://kopis.or.kr/openApi/restful/boxoffice?service={service_key}&ststype={ststype}&date={yesterday}&catecode=AAAA&area={area_code}"
    response = requests.get(url)

    # API 호출 성공 시 데이터 반환, 실패 시 에러 메시지 출력
    if response.status_code == 200:
        return response.content
    else:
        print(f"API 요청 실패: {response.status_code} (ststype={ststype}, area={area_code})")
        return None

# 서울(11) 지역의 데이터를 가져오는 함수
def fetch_seoul_boxoffice_data(ststype):
    region_ranked_data = []  # 서울 지역의 데이터를 저장할 리스트

    # 서울(11) 지역에 대한 데이터만 수집
    area_code = "11"  # 서울 지역 고정
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
                    region_ranked_data.append({
                        "play_id": perf_id,
                        "play_name": record.get("prfnm", ""),
                        "play_period": record.get("prfpd", ""),
                        "theater_nm": record.get("prfplcnm", ""),
                        "play_poster": f"https://www.kopis.or.kr{record.get('poster', '')}",
                        "rank": record.get("rnum", "")  # rnum 그대로 사용
                    })
        except Exception as e:
            print(f"XML 파싱 오류 (ststype={ststype}, area={area_code}): {e}")

    return region_ranked_data


# 뷰 함수
def home(request):
    # 서울(11) 지역의 데이터 가져오기
    ststype = "day"  # 예시로 "day"를 사용 (여기에 필요한 `ststype` 값을 넣을 수 있음)
    ranked_data = fetch_seoul_boxoffice_data(ststype)

    if request.user.is_authenticated:  # 로그인 여부 체크
        # 로그인 후 템플릿 렌더링
        return render(request, 'main/home.html', {'ranked_data': ranked_data})
    else:
        # 로그인 전에도 박스오피스 데이터 전달
        return render(request, 'main/before_login.html', {'ranked_data': ranked_data})  # 로그인 전 템플릿

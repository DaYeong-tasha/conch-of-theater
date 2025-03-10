import requests
import xmltodict
import json
import csv

# Kopis API 호출 URL, 공연 ID (mt20id)를 이용해 세부 정보를 불러옴
url = "https://www.kopis.or.kr/openApi/restful/pblprfr/{mt20id}"

# API 서비스 키 설정
service_key = "69d72dcef51346ba8fbc7b4acec944df"

# kopis_list.csv 파일에서 mt20id와 year 읽어오기
mt20ids = []  # 공연 ID를 저장할 리스트
year_dict = {}  # mt20id에 해당하는 year 값을 저장할 딕셔너리
with open("kopis_merged_list_250103_No_duplicates.csv", "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)  # CSV 파일을 딕셔너리 형태로 읽음
    for row in reader:
        mt20id = row["play_id"]
        year = row["year"]
        mt20ids.append(mt20id)  # 공연 ID 리스트에 추가
        year_dict[mt20id] = year  # year 값을 딕셔너리에 저장

# 이미 저장된 CSV 파일에서 마지막 mt20id를 확인
last_saved_mt20id = ""
try:
    with open("kopis_details_250103.csv", "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            last_saved_mt20id = row["play_id"]  # 마지막으로 저장된 play_id 추출
except FileNotFoundError:
    print("기존 CSV 파일이 없습니다. 새로 시작합니다.")

# 마지막 저장된 mt20id 이후부터 진행
start_index = mt20ids.index(last_saved_mt20id) + 1 if last_saved_mt20id else 0
remaining_mt20ids = mt20ids[start_index:]  # 남은 mt20id 리스트

# CSV 파일에 사용할 필드 이름(컬럼명) 정의
fieldnames = [
    "play_id", "play_name", "play_strdate", "play_enddate", "theater_nm", "play_forcast", "play_runtime",
    "play_age", "play_guidance", "play_poster", "loc", "play_status", "dtguidance", "child", "openrun", "festival",
    "styurls_1", "styurls_2", "styurls_3", "styurls_4",   # 스타일 URL 4개
    "relate_1", "relateurl_1", "relate_2", "relateurl_2",
    "relate_3", "relateurl_3", "relate_4", "relateurl_4",
    "relate_5", "relateurl_5", "relate_6", "relateurl_6",
    "relate_7", "relateurl_7", "relate_8", "relateurl_8",  # 예매처 이름 및 URL 8개
    "mt10id", "year"  # year 추가
]

# kopis_performance_details.csv 파일에 데이터를 기록
with open("kopis_details_250103.csv", "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # CSV writer 객체 생성
    # 이미 헤더가 있는 경우 첫 번째 줄을 건너뜁니다.
    if csvfile.tell() == 0:  # 파일이 비어 있을 경우 헤더 작성
        writer.writeheader()

    # 각 mt20id에 대해 API를 호출하고 세부 정보를 추출하여 CSV에 저장
    for mt20id in remaining_mt20ids:
        api_url = url.format(mt20id=mt20id)  # API 요청 URL 생성
        params = {"service": service_key}  # API 서비스 키를 파라미터에 포함
        response = requests.get(api_url, params=params)  # API 요청 전송

        # 응답 상태가 정상(200)일 경우 처리
        if response.status_code == 200:
            # XML 데이터를 JSON 형식으로 변환
            try:
                xml_data = xmltodict.parse(response.content)  # XML 파싱
                json_data = json.loads(json.dumps(xml_data))  # JSON 형식으로 변환
                performance = json_data.get("dbs", {}).get("db", {})  # 공연 상세 정보 추출

                if not performance:
                    print(f"mt20id {mt20id}에 대한 데이터를 찾을 수 없습니다.")
                    continue  # 데이터가 없을 경우 건너뜀

                # 각 공연 정보 딕셔너리 생성
                performance_data = {
                    "play_id": performance.get("mt20id", ""),  # 공연 ID
                    "play_name": performance.get("prfnm", ""),  # 공연명
                    "play_strdate": performance.get("prfpdfrom", ""),  # 공연 시작일
                    "play_enddate": performance.get("prfpdto", ""),  # 공연 종료일
                    "theater_nm": performance.get("fcltynm", ""),  # 공연 장소명
                    "play_forcast": performance.get("prfcast", ""),  # 출연진
                    "play_runtime": performance.get("prfruntime", ""),  # 공연 시간
                    "play_age": performance.get("prfage", ""),  # 관람 연령
                    "play_guidance": performance.get("pcseguidance", ""),  # 가격 안내
                    "play_poster": performance.get("poster", ""),  # 포스터 이미지 URL
                    "loc": performance.get("area", ""),  # 지역 (예: 서울, 대구 등)
                    "play_status": performance.get("prfstate", ""),  # 공연 상태 (예: 공연중, 종료 등)
                    "dtguidance": performance.get("dtguidance", ""),  # 공연 시간 안내 (요일별 시간)
                    "child": performance.get("child", ""), # 아이들 공연 여부
                    "openrun": performance.get("openrun", ""),  # 오픈런 여부
                    "festival": performance.get("festival", ""),  # 오픈런 여부
                    "mt10id":  performance.get("mt10id", ""),  # 아이들 공연 여부
                    "year": year_dict.get(mt20id, "")  # year 값을 추가 (없으면 빈 문자열)
                }

                # 스타일 URL을 최대 4개까지 styurls_1 ~ styurls_4 필드에 저장
                styurls = performance.get("styurls", {}).get("styurl", [])
                if isinstance(styurls, list):  # URL들이 리스트 형태일 때만 처리
                    for i in range(4):  # 최대 4개까지만 처리
                        performance_data[f"styurls_{i + 1}"] = styurls[i] if i < len(styurls) else ""
                else:
                    performance_data["styurls_1"] = styurls if styurls else ""  # 하나만 있을 경우 처리

                # 예매처 이름과 URL 정보를 최대 8개까지 relatenm_1 ~ relatenm_8, relateurl_1 ~ relateurl_8 필드에 저장
                relates = performance.get("relates", None)

                # relates가 None이거나 리스트가 아닐 경우 빈 리스트로 처리
                if not isinstance(relates, dict):
                    relates = {}

                # relate 목록을 처리하는 코드
                relate_list = relates.get("relate", [])

                # relate_list가 리스트인 경우
                if isinstance(relate_list, list):
                    for i in range(8):  # 최대 8개까지 처리
                        if i < len(relate_list) and isinstance(relate_list[i], dict):  # 리스트 내 요소가 딕셔너리인지 확인
                            performance_data[f"relate_{i + 1}"] = relate_list[i].get("relatenm", "")
                            performance_data[f"relateurl_{i + 1}"] = relate_list[i].get("relateurl", "")
                        else:
                            performance_data[f"relate_{i + 1}"] = ""  # 리스트 내 항목이 부족하면 빈 값 처리
                            performance_data[f"relateurl_{i + 1}"] = ""  # 리스트 내 항목이 부족하면 빈 값 처리
                else:
                    # 만약 relate가 리스트가 아니거나 비어 있으면 빈 값 처리
                    for i in range(8):
                        performance_data[f"relate_{i + 1}"] = ""
                        performance_data[f"relateurl_{i + 1}"] = ""

                # CSV 파일에 공연 정보를 기록
                writer.writerow(performance_data)

            except Exception as e:
                print(f"mt20id {mt20id} 처리 중 오류 발생: {e}")
        else:
            print(f"mt20id {mt20id}에 대한 API 요청 실패: {response.status_code}")

print("CSV 파일 저장 완료!")

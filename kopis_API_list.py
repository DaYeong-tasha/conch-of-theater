import requests
import xmltodict
import json
import csv
import os
from datetime import datetime

# 현재 날짜를 기준으로 실행일자 가져오기
today_date = datetime.now().strftime("%Y%m%d")

url = "https://www.kopis.or.kr/openApi/restful/pblprfr"
service_key = "69d72dcef51346ba8fbc7b4acec944df"

start_year = 2013  # 시작 연도
end_year = 2025    # 종료 연도
rows_per_page = 20

output_file = f"kopis_merged_list_{today_date}.csv"  # 병합된 파일명

# 병합된 데이터를 저장할 CSV 파일 생성
with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    fieldnames = ['play_id', 'play_name', 'play_strdate', 'play_enddate', 'theater_nm', 'year']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()  # 병합 파일의 헤더 추가

    for year in range(start_year, end_year + 1):
        stdate = f"{year}0101" if year != 2013 else "20130501"  # 2013년만 시작일이 다름
        eddate = f"{year}1231" if year != 2025 else "20250131"  # 2025년은 1월 말까지 포함
        current_page = 1
        input_file = f"kopis_list_{stdate}_{today_date}.csv"

        # 개별 연도 파일 저장
        with open(input_file, "w", newline="", encoding="utf-8") as csvfile:
            writer_year = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer_year.writeheader()

            while True:
                params = {
                    "service": service_key,
                    "stdate": stdate,
                    "eddate": eddate,
                    "rows": rows_per_page,
                    "cpage": current_page,
                    "shcate": "AAAA"
                }

                response = requests.get(url, params=params)

                if response.status_code == 200:
                    xml_data = xmltodict.parse(response.content)
                    json_data = json.loads(json.dumps(xml_data))

                    if "dbs" not in json_data or not json_data["dbs"]:
                        print(f"{year}년 {current_page} 페이지: 데이터가 없습니다.")
                        break

                    performances = json_data["dbs"].get("db")
                    if not performances:
                        print(f"{year}년 {current_page} 페이지: 공연 데이터가 없습니다.")
                        break

                    if isinstance(performances, dict):
                        performances = [performances]

                    for perf in performances:
                        # "theater_nm"은 "fcltynm" 또는 "shprfnmfct" 중 존재하는 값을 사용
                        theater_name = perf.get("fcltynm") or perf.get("shprfnmfct")
                        if not theater_name:
                            theater_name = "정보 없음"

                        row = {
                            "play_id": perf["mt20id"],
                            "play_name": perf["prfnm"],
                            "play_strdate": perf["prfpdfrom"],
                            "play_enddate": perf["prfpdto"],
                            "theater_nm": theater_name,
                            "year": year  # year 칼럼 추가
                        }
                        writer_year.writerow(row)  # 연도별 파일 저장
                        writer.writerow(row)  # 병합 파일에 바로 저장

                    print(f"{year}년 {current_page} 페이지 데이터 저장 완료")
                    current_page += 1
                else:
                    print(f"{year}년 API 요청 실패 또는 데이터 없음: {response.status_code}")
                    print("응답 내용:", response.text)
                    break

        print(f"{year}년 데이터 저장 완료!")

print("모든 데이터 저장 및 병합 완료!")

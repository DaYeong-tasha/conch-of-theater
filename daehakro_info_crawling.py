import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 기본 URL 설정
BASE_URL = "https://www.xn--vk1br5hppx9qddtd.com/board.do?command=openInfo_view&idx={}&p_retrieve_type=1&p_retrieve_key=&currentPage=1"

# 데이터를 저장할 리스트
data = []

def fetch_page_data(idx):
    """idx에 해당하는 페이지 데이터를 가져와 처리"""
    url = BASE_URL.format(idx)

    try:
        # SSL 인증 무시 및 요청
        response = requests.get(url, verify=False, timeout=10)

        if response.status_code != 200:
            print(f"Page with idx={idx} not found.")
            return None

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")

        # 연극명 추출
        title_span = soup.select_one("#viewcon > div > div.view-title > span")
        title = title_span.get_text(strip=True) if title_span else "No Title"

        # 작품 정보 찾기
        info_label = soup.find("span", string="※작품정보")
        if info_label:
            # 작품 정보가 있는 div 찾기
            info_div = None
            next_elem = info_label.find_next("div")

            while next_elem:
                if next_elem.find("span"):  # 작품 정보가 있는 span이 있으면 해당 div
                    info_div = next_elem
                    break
                next_elem = next_elem.find_next("div")

            # info_div가 제대로 찾았다면, 정보 추출
            if info_div:
                info = info_div.get_text(strip=True)
            else:
                info = "No Info"
        else:
            # 작품 정보도 못 찾았을 경우 공연 줄거리 위치 확인
            story_start = soup.select_one(
                "#viewcon > div > div:nth-child(4) > div > div:nth-child(2) > div > div > div > div > div > div:nth-child(11)"
            )
            story_end = soup.select_one(
                "#viewcon > div > div:nth-child(4) > div > div:nth-child(2) > div > div > div > div > div > div:nth-child(12)"
            )

            if story_start and story_end:
                story_content = []
                current_div = story_start.find_next_sibling("div")
                while current_div and current_div != story_end:
                    story_content.append(current_div.get_text(strip=True))
                    current_div = current_div.find_next_sibling("div")
                info = " ".join(story_content) if story_content else "No Story"
            else:
                info = ""

        # 출연진 정보 크롤링 (기존 위치)
        cast_start = soup.select_one(
            "#viewcon > div > div:nth-child(4) > div > div:nth-child(23)"
        )
        cast_end = soup.select_one(
            "#viewcon > div > div:nth-child(4) > div > div:nth-child(24)"
        )

        if cast_start and cast_end:
            cast_content = []
            current_div = cast_start.find_next_sibling("div")
            while current_div and current_div != cast_end:
                cast_content.append(current_div.get_text(strip=True))
                current_div = current_div.find_next_sibling("div")
            cast = " ".join(cast_content) if cast_content else "No Cast Info"
        else:
            # 기존 위치도 못 찾았을 경우 새로운 div 영역에서 탐색
            alt_start = soup.select_one(
                "#viewcon > div > div:nth-child(4) > div > div:nth-child(2) > div > div > div > div > div > div:nth-child(11)"
            )
            alt_end = soup.select_one(
                "#viewcon > div > div:nth-child(4) > div > div:nth-child(2) > div > div > div > div > div > div:nth-child(24)"
            )

            if alt_start and alt_end:
                alt_content = []
                current_div = alt_start.find_next_sibling("div")
                while current_div and current_div != alt_end:
                    alt_content.append(current_div.get_text(strip=True))
                    current_div = current_div.find_next_sibling("div")
                cast = " ".join(alt_content) if alt_content else "No Alt Cast Info"
            else:
                cast = ""

        return {"idx": idx, "title": title, "info": info, "cast": cast}

    except requests.exceptions.RequestException as e:
        print(f"Request failed for idx={idx}: {e}")
        return None

# 첫 번째 idx 값 설정
idx = 2709

while idx > 0:
    page_data = fetch_page_data(idx)

    if page_data:
        data.append(page_data)
        print(f"Scraped idx={idx}: {page_data['title']}")
    else:
        print(f"Stopping at idx={idx}. Page not found.")
        break  # 페이지를 찾을 수 없으면 크롤링 종료

    idx -= 1  # idx 감소
    time.sleep(1)  # 서버 부하 방지

# 데이터프레임 생성 및 CSV로 저장
df = pd.DataFrame(data)
df.to_csv("theater_info_try5.csv", index=False, encoding="utf-8-sig")
print("Data saved to theater_info-try5.csv")

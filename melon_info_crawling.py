
#페이지 자동으로 넘어가게 코드를 안짜서 페이지 하나하나 코드 반복해서 적용함

import time
import os
import pandas as pd
from selenium import webdriver
from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 크롬 옵션 설정
options = Options()
options.add_argument("--start-maximized")  # 브라우저 최대화
options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화

# WebDriver 생성
service = Service(ChromeDriverManager().install())  # WebDriver Manager로 크롬드라이버 자동 설치
driver = webdriver.Chrome(service=service, options=options)

# 주소는 Melon Ticket
url = "https://ticket.melon.com/csoon/index.htm#orderType=0&pageIndex=1&schGcode=GENRE_ALL&schText=&schDt="
driver.get(url)
time.sleep(3)  # 3초 정지

# 티켓 오픈 소식에서 검색
try:
    # 검색어 입력란에 "연극" 입력
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "schText"))
    )
    search_input.clear()
    search_input.send_keys("연극")

    # 검색 버튼 클릭
    search_button = driver.find_element(By.CLASS_NAME, "ticket_button")
    search_button.click()

    # 검색 결과 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "list_ticket_cont"))
    )

    # 게시글 상세 정보를 저장할 리스트 및 중복 확인용 집합
    post_details = []
    seen_texts = set()  # 중복 확인용 집합

    # 저장 개수 제한
    MAX_COUNT = 100

    # 모든 게시글 리스트 가져오기
    while len(post_details) < MAX_COUNT:
        try:
            post_links = driver.find_elements(By.XPATH, "//div[@class='link_consert']/a[@class='tit']")

            for i, link in enumerate(post_links):
                if len(post_details) >= MAX_COUNT:
                    break

                try:
                    # 게시글 리스트를 새로 가져오기 (각 게시글 클릭 전)
                    post_links = driver.find_elements(By.XPATH, "//div[@class='link_consert']/a[@class='tit']")
                    title = post_links[i].text  # 공연 제목 저장
                    print(f"게시글 {i + 1} 클릭 중: {title}")

                    # 링크 클릭
                    post_links[i].click()

                    # 공연 소개 부분 가져오기
                    intro_text = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "concert_info_txt"))
                    ).text

                    # 중복 확인 후 저장
                    if intro_text not in seen_texts:
                        post_details.append({"공연 이름": title, "공연 소개": intro_text})
                        seen_texts.add(intro_text)  # 중복 확인용 집합에 추가
                        print(f"게시글 {i + 1} 수집 완료.")
                    else:
                        print(f"게시글 {i + 1} 중복됨. 저장하지 않음.")

                    # 뒤로가기
                    driver.back()

                    # 검색 결과 대기
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "list_ticket_cont"))
                    )
                except (StaleElementReferenceException, TimeoutException) as e:
                    print(f"게시글 {i + 1} 처리 중 오류: {e}")
                    continue

            # 수집 완료 후 루프 종료
            break

        except Exception as e:
            print(f"게시글 리스트 처리 중 오류: {e}")
            continue

    # 출력 및 CSV 저장
    if post_details:
        df = pd.DataFrame(post_details)
        file_name = "공연_소개_목록.csv"
        df.to_csv(file_name, index=False, encoding="utf-8-sig")

        # 저장된 CSV 파일의 절대 경로 출력
        file_path = os.path.abspath(file_name)
        print(f"공연 소개 내용을 '{file_path}' 파일로 저장했습니다.")

finally:
    # 브라우저 종료
    driver.quit()





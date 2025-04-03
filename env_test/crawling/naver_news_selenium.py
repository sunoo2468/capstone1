from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# 크롬 드라이버 경로 설정 (너한테 맞게 수정!)
CHROMEDRIVER_PATH = "/opt/homebrew/bin/chromedriver"

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# 네이버 뉴스 검색 결과 페이지 열기
query = "인공지능"
url = f"https://search.naver.com/search.naver?where=news&query={query}"
driver.get(url)
time.sleep(2)  # 페이지 로딩 대기

# 뉴스 제목과 링크 추출
articles = driver.find_elements(By.CSS_SELECTOR, "a.news_tit")

for a in articles:
    title = a.get_attribute("title")
    link = a.get_attribute("href")
    print("제목:", title)
    print("링크:", link)
    print("-" * 40)

driver.quit()

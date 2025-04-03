from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import json

# 1. 뉴스 제목 담을 리스트 초기화
titles = []

# 2. 크롬 옵션 설정
options = Options()
driver_path = "/opt/homebrew/bin/chromedriver"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 3. CNN 페이지 열기
driver.get("https://edition.cnn.com/world")
time.sleep(5)

# 4. selector로 뉴스 추출
articles = driver.find_elements(By.CSS_SELECTOR, "a.container__link")

print("✅ CNN 뉴스 기사 제목과 링크:\n")
count = 0
for article in articles:
    title = article.text.strip()
    link = article.get_attribute("href")

    # 링크 보정
    if title and link and link.startswith("/"):
        link = "https://edition.cnn.com" + link

    # 저장 조건 확인 후 리스트에 append
    if title and link and "cnn.com" in link:
        print(f"제목: {title}")
        print(f"링크: {link}\n")
        titles.append(title)  # ✅ 여기서 리스트에 추가!!
        count += 1

    if count >= 10:
        break

# 5. 경로 설정 후 저장
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(base_dir, "data", "cnn_titles.json")

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(titles, f, ensure_ascii=False, indent=2)

driver.quit()

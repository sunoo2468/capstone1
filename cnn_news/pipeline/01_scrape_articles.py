# pipeline/scrape_cnn_full_sections.py

import os
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 루트 디렉토리 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
sys.path.append(ROOT_DIR)

# 저장 폴더 생성
os.makedirs(DATA_DIR, exist_ok=True)

# 크롬 드라이버 세팅
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# CNN 전체 섹션 리스트
CNN_SECTIONS = [
    "https://edition.cnn.com/us",
    "https://edition.cnn.com/world",
    "https://edition.cnn.com/politics",
    "https://edition.cnn.com/business",
    "https://edition.cnn.com/health",
    "https://edition.cnn.com/entertainment",
    "https://edition.cnn.com/style",
    "https://edition.cnn.com/travel",
    "https://edition.cnn.com/sport",
    "https://edition.cnn.com/science",
    "https://edition.cnn.com/climate",
    "https://edition.cnn.com/weather",
    "https://edition.cnn.com/europe/ukraine-russia",
    "https://edition.cnn.com/middleeast/israel-hamas-war",
    "https://edition.cnn.com/gaming"
]

def scroll_down(times=3):
    for _ in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

def collect_article_links(section_url, max_links=30):
    """
    섹션별 기사 링크 수집
    """
    driver.get(section_url)
    time.sleep(3)
    scroll_down(times=3)

    links = []
    elements = driver.find_elements(By.CSS_SELECTOR, "a.container__link")

    for elem in elements:
        try:
            link = elem.get_attribute("href")
            if link and "2024" in link and "/videos/" not in link:
                links.append(link)
            if len(links) >= max_links:
                break
        except Exception as e:
            print(f"❌ 링크 파싱 에러: {e}")

    return links

def extract_article_content(url):
    """
    기사 본문 텍스트 추출
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        paragraphs = soup.find_all("div", class_="paragraph")
        if not paragraphs:
            paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text
    except Exception as e:
        print(f"❌ 본문 추출 실패: {e}")
        return ""

def scrape_cnn_full_sections():
    all_articles = []

    for section_url in CNN_SECTIONS:
        print(f"🌎 {section_url} 섹션 시작...")
        links = collect_article_links(section_url, max_links=30)

        for link in links:
            try:
                content = extract_article_content(link)
                title = driver.title
                article = {
                    "title": title,
                    "url": link,
                    "content": content
                }
                all_articles.append(article)
            except Exception as e:
                print(f"❌ 기사 처리 실패: {e}")

    return all_articles

def remove_duplicate_articles(articles):
    seen = set()
    unique_articles = []
    for article in articles:
        key = (article.get("title", "").strip(), article.get("url", "").strip())
        if key not in seen:
            seen.add(key)
            unique_articles.append(article)
    return unique_articles

if __name__ == "__main__":
    # 크롤링
    articles = scrape_cnn_full_sections()

    # 중복 제거
    articles = remove_duplicate_articles(articles)

    save_path = os.path.join(DATA_DIR, "cnn_articles_raw.json")

    with open(save_path, "w") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(articles)}개 기사 저장 완료!")

    driver.quit()

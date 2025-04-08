from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import time

def scrape_cnn_articles_daily(max_articles=100):
    """
    CNN 메인 페이지에서 날짜 기반 뉴스 기사 본문을 최대 max_articles개 수집
    """
    base_url = "https://edition.cnn.com"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    time.sleep(5)

    # 날짜 패턴 포함된 뉴스 기사 링크만 추출
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/2024/'], a[href*='/2025/']")
    article_links = list(set([
        link.get_attribute("href")
        for link in links
        if link.get_attribute("href") and "cnn.com" in link.get_attribute("href") and "html" in link.get_attribute("href")
    ]))

    print(f"🔗 유효한 링크 수: {len(article_links)}")

    articles = []

    for link in article_links:
        try:
            driver.get(link)
            time.sleep(1.5)

            title = driver.title
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            content = "\n".join([p.text for p in paragraphs if p.text.strip()])

            if len(content) > 500:  # 본문 길이 필터
                articles.append({
                    "url": link,
                    "title": title,
                    "content": content,
                    "date": datetime.today().strftime("%Y-%m-%d")
                })

            if len(articles) >= max_articles:
                break

        except Exception as e:
            print(f"❌ 오류 발생 링크: {link} — {e}")
            continue

    driver.quit()
    print(f"✅ 최종 수집된 기사 수: {len(articles)}")
    return articles

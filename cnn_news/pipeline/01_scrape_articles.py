import json
import sys, os

# cnn_news 루트 디렉토리 경로 계산
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")

sys.path.append(ROOT_DIR)

from utils.cnn_scraper_selenium import scrape_cnn_articles_daily

if __name__ == "__main__":
    articles = scrape_cnn_articles_daily(max_articles=100)

    # 항상 cnn_news/data 경로에 저장되도록 고정
    os.makedirs(DATA_DIR, exist_ok=True)
    save_path = os.path.join(DATA_DIR, "cnn_articles_raw.json")
    
    with open(save_path, "w") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(articles)}개 기사 저장 완료!")
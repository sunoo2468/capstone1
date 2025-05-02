# pipeline/03_extract_keywords.py

import json
import os
import sys
from keybert import KeyBERT

# 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
sys.path.append(ROOT_DIR)

INPUT_FILE = os.path.join(DATA_DIR, "cnn_articles_with_sentiment.json")  # 원본
OUTPUT_FILE = os.path.join(DATA_DIR, "cnn_keywords_bert.json")            # 수정된 파일

# KeyBERT 모델 로드
kw_model = KeyBERT(model="all-MiniLM-L6-v2")

def load_articles(path):
    with open(path, "r") as f:
        return json.load(f)

def save_articles(articles, path):
    with open(path, "w") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"✅ 키워드 저장 완료 → {path}")

def extract_keywords_from_articles(articles, top_n=5):
    updated_articles = []
    for article in articles:
        title = article.get("title", "")
        content = article.get("content", "")
        sentiment = article.get("sentiment", {})

        if content.strip():
            keywords = kw_model.extract_keywords(
                content,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                use_maxsum=True,
                nr_candidates=20,
                top_n=top_n
            )
            keyword_list = [kw for kw, score in keywords]
        else:
            keyword_list = []

        # content와 url은 아예 제외하고 저장
        updated_articles.append({
            "title": title,
            "sentiment": sentiment,
            "keywords": keyword_list
        })

    return updated_articles

def main():
    articles = load_articles(INPUT_FILE)
    articles_with_keywords = extract_keywords_from_articles(articles)
    save_articles(articles_with_keywords, OUTPUT_FILE)

if __name__ == "__main__":
    main()

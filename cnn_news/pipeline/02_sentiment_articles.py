import json
import os
import sys

# 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")

sys.path.append(ROOT_DIR)
from extraction.sentiment_analysis import analyze_sentiment

def load_articles(path):
    with open(path, "r") as f:
        return json.load(f)

def save_articles(articles, path):
    with open(path, "w") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"✅ 저장 완료: {len(articles)}개 → {path}")

def add_sentiment_to_articles(articles):
    for article in articles:
        article["sentiment"] = analyze_sentiment(article["content"])
    return articles

def main():
    input_path = os.path.join(DATA_DIR, "cnn_articles_raw.json")
    output_path = os.path.join(DATA_DIR, "cnn_articles_with_sentiment.json")

    articles = load_articles(input_path)
    articles = add_sentiment_to_articles(articles)
    save_articles(articles, output_path)

    return articles

if __name__ == "__main__":
    main()

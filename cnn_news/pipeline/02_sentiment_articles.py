import json
import os, sys

# cnn_news 최상단 디렉토리 경로 계산
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")

sys.path.append(ROOT_DIR)

from extraction.sentiment_analysis import analyze_sentiment

# 원본 기사 로드
input_path = os.path.join(DATA_DIR, "cnn_articles_raw.json")
with open(input_path, "r") as f:
    articles = json.load(f)

# 감성 분석 수행
for article in articles:
    sentiment = analyze_sentiment(article["content"])
    article["sentiment"] = sentiment

# 결과 저장
output_path = os.path.join(DATA_DIR, "cnn_articles_with_sentiment.json")
with open(output_path, "w") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print(f"✅ 감성 분석된 기사 수: {len(articles)}")

import os
import json
import spacy
from collections import Counter

# ✅ 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")

INPUT_PATH = os.path.join(DATA_DIR, "cnn_articles_with_sentiment.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "cnn_keywords_spacy.json")

# ✅ spaCy 모델 로드 (최초 1회 다운로드 필요: python -m spacy download en_core_web_lg)
nlp = spacy.load("en_core_web_lg")

def extract_keywords(text, top_k=10):
    """
    문장에서 noun chunks 기반 주요 키워드 top_k개 추출
    """
    doc = nlp(text)
    chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks if len(chunk.text) > 1]
    counter = Counter(chunks)
    keywords = [kw for kw, _ in counter.most_common(top_k)]
    return keywords

# ✅ 데이터 로드
with open(INPUT_PATH, "r") as f:
    data = json.load(f)

results = []

for article in data:
    if article["sentiment"]["label"] != "POSITIVE":
        continue  # 긍정 뉴스만 사용

    keywords = extract_keywords(article["content"], top_k=10)

    results.append({
        "url": article["url"],
        "title": article["title"],
        "date": article["date"],
        "keywords": keywords
    })

# ✅ 저장
with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"✅ 저장 완료: {OUTPUT_PATH}")

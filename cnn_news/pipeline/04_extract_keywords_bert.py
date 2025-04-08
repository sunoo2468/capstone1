# pipeline/04_extract_keywords_bert.py

import os
import json
from sentence_transformers import SentenceTransformer, util

# 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")

INPUT_PATH = os.path.join(DATA_DIR, "cnn_keywords_spacy.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "cnn_keywords_bert.json")

# 모델 로드
print("🧠 Loading Sentence-BERT model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# 데이터 불러오기
with open(INPUT_PATH, "r") as f:
    articles = json.load(f)

results = []

for article in articles:
    candidates = article.get("keywords", [])
    if not candidates:
        continue

    # 문서 전체를 하나의 string으로 만들기
    doc_text = article.get("title", "") + "\n" + article.get("content", "")

    # 임베딩
    doc_embedding = model.encode(doc_text, convert_to_tensor=True)
    keyword_embeddings = model.encode(candidates, convert_to_tensor=True)

    # 유사도 계산
    scores = util.cos_sim(doc_embedding, keyword_embeddings)[0]
    top_indices = scores.topk(k=min(5, len(candidates))).indices.tolist()

    top_keywords = [candidates[i] for i in top_indices]

    results.append({
        "url": article["url"],
        "title": article["title"],
        "date": article["date"],
        "keywords": top_keywords
    })

# 저장
with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ 핵심 키워드 추출 완료! 총 {len(results)}개 문서 저장됨.")

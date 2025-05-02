# pipeline/04_match_industry_from_news.py

import os
import sys
import json

# 루트 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
MAPPING_DIR = os.path.join(DATA_DIR, "mapping")

sys.path.append(ROOT_DIR)

# 경로 설정
input_path = os.path.join(DATA_DIR, "cnn_articles_with_sentiment.json")
industry_mapping_path = os.path.join(MAPPING_DIR, "industry_keyword_mapping.json")
output_path = os.path.join(DATA_DIR, "cnn_articles_with_industry.json")

# 파일 로드 함수
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

# 파일 저장 함수
def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 본문에서 산업 키워드 매칭
def match_industries_in_article(content, industry_mapping):
    matched = set()
    content_lower = content.lower()
    for industry, keywords in industry_mapping.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                matched.add(industry)
                break  # 하나라도 매칭되면 해당 산업으로 인정
    return list(matched)

def main():
    # 데이터 로드
    articles = load_json(input_path)
    industry_mapping = load_json(industry_mapping_path)

    # 뉴스별 산업 매칭
    for article in articles:
        content = article.get("content", "")
        matched_industries = match_industries_in_article(content, industry_mapping)
        article["matched_industries"] = matched_industries

    # 저장
    save_json(articles, output_path)
    print(f"✅ {len(articles)}개 뉴스에 산업 매칭 완료: {output_path}")

if __name__ == "__main__":
    main()
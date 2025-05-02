# pipeline/map_company_vectors.py
"""
기사 JSON에 company_mentions 필드 추가
실행 예)
python -m pipeline.map_company_vectors \
       --articles data/cnn/cnn_articles_with_sentiment.json \
       --companies data/collect_company/final_company_list.csv \
       --vectors  data/embeddings/company_vectors.json \
       --out      data/cnn/cnn_articles_with_industry_and_company.json
"""
import argparse, json, csv, re, unicodedata, numpy as np
from pathlib import Path
from rapidfuzz import process, fuzz

# ---------- 공통 유틸 ----------
def normalize(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", txt)
    txt = re.sub(r"[^0-9A-Za-z가-힣]", " ", txt.upper())
    return re.sub(r"\s+", " ", txt).strip()

# ---------- 매인 ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--articles", required=True)
    ap.add_argument("--companies", required=True)
    ap.add_argument("--vectors", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # 1) 회사명 ↔ 티커 매핑
    comp2tkr = {}
    with open(args.companies, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            comp2tkr[normalize(row["기업명"])] = row["Ticker"].upper()

    # 2) 티커 ↔ 벡터
    with open(args.vectors, encoding="utf-8") as f:
        tkr2vec = json.load(f)
    keys = list(comp2tkr.keys())           # fuzzy 검색용

    # 3) 기사 적용
    with open(args.articles, encoding="utf-8") as f:
        arts = json.load(f)

    for art in arts:
        mentions = []
        for org in art.get("org_entities", []):
            n = normalize(org)
            # (a) 회사명 exact / fuzzy 매칭 → 티커
            if n in comp2tkr:
                tkr = comp2tkr[n]
            else:
                best, score, _ = process.extractOne(
                    n, keys, scorer=fuzz.token_set_ratio)
                tkr = comp2tkr[best] if score >= 90 else None
            # (b) 티커 → 벡터 붙이기
            vec = tkr and tkr2vec.get(tkr)
            if vec:
                mentions.append({"name": org, "ticker": tkr, "vector": vec})
        art["company_mentions"] = mentions

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(arts, f, ensure_ascii=False, indent=2)
    print(f"✅ 저장 완료 → {args.out}")

if __name__ == "__main__":
    main()

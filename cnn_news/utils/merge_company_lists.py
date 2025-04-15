# utils/merge_company_list.py

import pandas as pd
import os

# 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "collect_company")
os.makedirs(DATA_DIR, exist_ok=True)

# 파일 경로
krx_path = os.path.join(DATA_DIR, "krx_company_list.csv")
nasdaq_path = os.path.join(DATA_DIR, "nasdaq_company_list.csv")
unicorn_path = os.path.join(DATA_DIR, "unicorn_company_list.csv")
save_path = os.path.join(DATA_DIR, "final_company_list.csv")

# 파일 로드
krx = pd.read_csv(krx_path)[["기업명"]].copy()
nasdaq = pd.read_csv(nasdaq_path)[["기업명"]].copy()
unicorn = pd.read_csv(unicorn_path)[["기업명"]].copy()

# 출처 컬럼 추가
krx["출처"] = "KRX"
nasdaq["출처"] = "NASDAQ"
unicorn["출처"] = "UNICORN"

# 병합
merged = pd.concat([krx, nasdaq, unicorn], ignore_index=True)

# 이상치 제거
filtered = merged[~merged["기업명"].str.lower().str.contains(
    "about|floor|avenue|unnamed|resources|customers|privacy|terms", na=False)]
filtered = filtered[filtered["기업명"].str.len() <= 50]

# 중복 처리: 출처 병합
merged_cleaned = (
    filtered.groupby("기업명")["출처"]
    .apply(lambda x: ",".join(sorted(set(x))))
    .reset_index()
)

# 저장
merged_cleaned.to_csv(save_path, index=False, encoding="utf-8-sig")
print(f"✅ 최종 기업 리스트 저장 완료 → {save_path}")

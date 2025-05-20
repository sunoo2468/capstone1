# score_companies.py (실전 프로젝트 버전, projector 완전 제거)

import os
import numpy as np
import pandas as pd
import json
import joblib

# ========== 1. 경로 셋팅 ==========
CUR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
emb_path = os.path.join(CUR_DIR, 'data', "glove_pca_64d.npy")    # (N, 64)
vocab_path = os.path.join(CUR_DIR, 'data', "industry_vocab.json")
company_csv = os.path.join(CUR_DIR, 'data', "nasdaq_screener_1744184912302.csv")
predictor_path = os.path.join(CUR_DIR, 'models', "promise_predictor.pkl")

# ========== 2. 산업 임베딩/키워드 로딩 ==========
industry_emb = np.load(emb_path)                                 # (N, 64)
with open(vocab_path, "r") as f:
    industry_vocab = json.load(f)
industry_vocab = [k.lower() for k in industry_vocab]

# ========== 3. 기업 데이터 로딩 ==========
companies = pd.read_csv(company_csv)

# ========== 4. 예측기 모델 로딩 ==========
promise_predictor = joblib.load(predictor_path)                  # 32차원 input이어야 함!

# ========== 5. 기업별 임베딩 생성 함수 ==========
def get_company_emb(industry_str):
    inds = []
    for vocab in industry_vocab:
        if pd.isna(industry_str): continue
        if vocab in industry_str.lower():
            inds.append(industry_vocab.index(vocab))
    if not inds:
        return None
    inds_emb = industry_emb[inds]         # (n, 64)
    inds_emb = inds_emb[:, :32]           # (n, 32) <<== 32차원만 사용!
    avg_emb = inds_emb.mean(axis=0)       # (32,)
    return avg_emb

# ========== 6. 유망도 예측 ==========
results = []
for idx, row in companies.iterrows():
    symbol = row["Symbol"]
    name = row.get("Name", "")
    industry_str = row["Industry"]
    comp_emb = get_company_emb(industry_str)
    if comp_emb is None:
        continue
    score = promise_predictor.predict(comp_emb.reshape(1, -1))[0]
    results.append({
        "Symbol": symbol,
        "Name": name,
        "Industry": industry_str,
        "PromiseScore": score
    })

df_result = pd.DataFrame(results)
df_result = df_result.sort_values("PromiseScore", ascending=False)
result_path = os.path.join(CUR_DIR, 'results', "company_promise_score.csv")
os.makedirs(os.path.dirname(result_path), exist_ok=True)
df_result.to_csv(result_path, index=False, encoding="utf-8-sig")
print(df_result.head(15))

import numpy as np
import pandas as pd
import json
import joblib
import os

# ====== 경로 세팅 ======
BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH    = os.path.join(BASE_DIR, 'data', 'cnn_news.db')
VOCAB_PATH = os.path.join(BASE_DIR, 'data', 'industry_vocab.json')
OUT_CSV    = os.path.join(BASE_DIR, 'data', 'industry_promise.csv')
CUR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
emb_path = os.path.join(CUR_DIR, 'data', "industry_emb_32d.npy")
vocab_path = os.path.join(CUR_DIR, 'data', "industry_vocab.json")
comp_path = os.path.join(CUR_DIR, 'data', "nasdaq_screener_1744184912302.csv")
model_path = os.path.join(CUR_DIR, 'models',"promise_predictor.pkl")
output_path = os.path.join(CUR_DIR, 'results', "company_promise_score.csv")

# ====== 임베딩 & vocab 불러오기 ======
industry_emb = np.load(emb_path)  # (산업개수, 32)
with open(vocab_path, "r") as f:
    industry_vocab = json.load(f)
industry2idx = {v.lower(): i for i, v in enumerate(industry_vocab)}

# ====== 기업 CSV 불러오기 ======
companies = pd.read_csv(comp_path)
# 컬럼 예시: Symbol, Name, Industry

# ====== 기업 임베딩 생성 함수 ======
def extract_industries(industry_str):
    if pd.isnull(industry_str):
        return []
    return [x.strip().lower() for x in industry_str.split(",")]

def get_company_emb(inds):
    idxs = [industry2idx[ind] for ind in inds if ind in industry2idx]
    if len(idxs) == 0:
        return np.zeros(industry_emb.shape[1])
    return np.mean(industry_emb[idxs], axis=0)

# ====== 전체 기업 임베딩 생성 ======
company_emb_list = []
for _, row in companies.iterrows():
    inds = extract_industries(row['Industry'])
    emb = get_company_emb(inds)
    company_emb_list.append(emb)
company_embs = np.stack(company_emb_list)  # (기업수, 32)

# ====== 유망도 예측 ======
predictor = joblib.load(model_path)
scores = predictor.predict(company_embs)
companies['promise_score'] = scores

# ====== 결과 저장 ======
companies.to_csv(output_path, index=False)
print(f'>> 결과 저장 완료: {output_path}')
print(companies[['Name', 'Industry', 'promise_score']].sort_values('promise_score', ascending=False).head(20))

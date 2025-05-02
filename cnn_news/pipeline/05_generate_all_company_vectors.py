# pipeline/generate_all_company_vectors.py
"""
티커 목록(ticker_list.json)을 읽어 GloVe 기반 기업 벡터(.npy) 생성
"""

import os, sys, json, numpy as np
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
sys.path.append(ROOT_DIR)

from utils.generate_company_vector import generate_company_vector_from_ticker
from utils.embedding_glove_loader import load_glove_embeddings

# --- 경로 설정 -------------------------------------------------
VEC_DIR  = os.path.join(DATA_DIR, "company_vectors")
MAP_DIR  = os.path.join(DATA_DIR, "mapping")
os.makedirs(VEC_DIR, exist_ok=True)

# --- 티커 목록 로드 -------------------------------------------------
ticker_path = os.path.join(MAP_DIR, "ticker_list.json")
with open(ticker_path, "r", encoding="utf-8") as f:
    tickers = json.load(f)  # 예: ["AAPL", "MSFT", "TSLA", ...]

# --- GloVe 임베딩 로드 -------------------------------------------------
glove_path = os.path.join(DATA_DIR, "collect_company", "glove.6B.300d.txt")
glove = load_glove_embeddings(glove_path)
print(f"✅ GloVe 단어 {len(glove)}개 로드 완료")

# --- 기업 벡터 생성 -------------------------------------------------
success, fail = 0, 0

for tkr in tickers:
    try:
        vec = generate_company_vector_from_ticker(tkr, glove)
        if vec is not None:
            np.save(os.path.join(VEC_DIR, f"{tkr}.npy"), vec)
            print(f"{tkr} 저장")
            success += 1
        else:
            print(f"{tkr} 실패")
            fail += 1
    except Exception as e:
        print(f"{tkr} 처리 중 오류 발생: {e}")
        fail += 1

print(f"\n 총 시도: {len(tickers)}개 | 성공: {success}개 | 실패: {fail}개")

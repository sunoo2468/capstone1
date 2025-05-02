# pipeline/generate_all_company_vectors.py

import sys
import os

# 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
sys.path.append(ROOT_DIR)

import numpy as np
import json
from utils.generate_company_vector import generate_company_vector_from_ticker
from utils.embedding_glove_loader import load_glove_embeddings

# 디렉토리 설정
save_vector_dir = os.path.join(DATA_DIR, "company_vectors")
save_mapping_dir = os.path.join(DATA_DIR, "mapping")
os.makedirs(save_vector_dir, exist_ok=True)
os.makedirs(save_mapping_dir, exist_ok=True)

# GloVe 로딩
glove_path = os.path.join(DATA_DIR, "collect_company", "glove.6B.300d.txt")
glove_embeddings = load_glove_embeddings(glove_path)

# 티커 리스트 예시 (나중엔 NASDAQ 전체로 변경)
tickers = ["AAPL", "MSFT", "AMZN", "GOOG", "META"]

ticker_list = []
vector_count = 0

for ticker in tickers:
    company_vector = generate_company_vector_from_ticker(ticker, glove_embeddings)
    if company_vector is not None:
        save_path = os.path.join(save_vector_dir, f"{ticker}.npy")
        np.save(save_path, company_vector)
        ticker_list.append(ticker)
        vector_count += 1
        print(f"✅ {ticker} 저장 완료")
    else:
        print(f"⚠️ {ticker} 벡터 생성 실패")

# 티커 리스트 저장
with open(os.path.join(save_mapping_dir, "ticker_list.json"), "w") as f:
    json.dump(ticker_list, f)

print(f"\n✅ 전체 벡터 생성 완료: {vector_count}/{len(tickers)}개 저장")

# make_promise_labels.py

import os
import json
import logging

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler

# ────── 설정 ──────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 1) 경로 설정
BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH    = os.path.join(BASE_DIR, 'data', 'cnn_news.db')
VOCAB_PATH = os.path.join(BASE_DIR, 'data', 'industry_vocab.json')
OUT_CSV    = os.path.join(BASE_DIR, 'data', 'industry_promise.csv')

# 2) 긍정 뉴스 DB 로드
engine = create_engine(f'sqlite:///{DB_PATH}')
df = pd.read_sql_table('cnn_positive_news', engine)
logger.info(f"Loaded {len(df)} positive news articles from DB")

# 3) 산업 키워드 목록 로드
with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
    industries = json.load(f)
logger.info(f"Loaded {len(industries)} industries from vocab")

# 4) 피처 계산
records = []
for idx, kw in enumerate(industries):
    mask    = df['industry_keys'].str.contains(fr'\b{kw}\b', case=False, na=False)
    df_kw   = df[mask]
    freq    = len(df_kw)
    # positive_orgs 컬럼은 comma-separated 심볼; 길이 > 0 이면 '기업 언급 동시'
    pos_rate = (df_kw['positive_orgs'].str.len() > 0).mean() if freq > 0 else 0.0
    records.append((idx, freq, pos_rate))

logger.info("Calculated raw features (freq, pos_rate) for each industry")

# 5) 표준화 & 가중합 레이블 생성
arr    = np.array([[r[1], r[2]] for r in records], dtype=float)
scaler = StandardScaler().fit(arr)
scaled = scaler.transform(arr)

# 예시 가중합: 0.7*freq_z + 0.3*pos_rate_z
weights = np.array([0.7, 0.3])
labels  = (scaled * weights).sum(axis=1)

logger.info("Standardized features and computed promise_label via weighted sum")

# 6) CSV로 저장
out_df = pd.DataFrame({
    'industry_id'   : [r[0] for r in records],
    'promise_label' : labels,
    'feat_freq'     : arr[:, 0],
    'feat_pos_rate' : arr[:, 1]
})
out_df.to_csv(OUT_CSV, index=False)
logger.info(f"Saved promise labels to {OUT_CSV} ({len(out_df)} rows)")

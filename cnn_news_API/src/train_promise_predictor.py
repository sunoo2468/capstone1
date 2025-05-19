# train_promise_predictor.py

import os
import json
import logging

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split
import joblib

# ────── 설정 ──────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 1) 경로 설정
BASE_DIR       = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EMBED_PATH     = os.path.join(BASE_DIR, 'data', 'industry_emb_32d.npy')
VOCAB_PATH     = os.path.join(BASE_DIR, 'data', 'industry_vocab.json')
LABEL_CSV_PATH = os.path.join(BASE_DIR, 'data', 'industry_promise.csv')
OUT_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'promise_predictor.pkl')

# 2) 데이터 로드
logger.info("Loading embeddings and labels...")
embeddings = np.load(EMBED_PATH)  # shape (N, 32)
with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
    vocab = json.load(f)          # len(vocab) == embeddings.shape[0]
labels_df = pd.read_csv(LABEL_CSV_PATH)

# 3) 피처(X)와 레이블(y) 준비
ids   = labels_df['industry_id'].astype(int).values
X_all = embeddings[ids]                 # (M, 32)
y_all = labels_df['promise_label'].values  # (M,)

logger.info(f"Prepared X_all shape={X_all.shape}, y_all shape={y_all.shape}")

# 4) 학습/테스트 분할
X_train, X_test, y_train, y_test = train_test_split(
    X_all, y_all, test_size=0.2, random_state=42
)
logger.info(f"Train/Test split: {len(X_train)}/{len(X_test)}")

# 5) 모델 학습 (Ridge Regression)
model = Ridge(alpha=1.0)
model.fit(X_train, y_train)
logger.info("Ridge regression model training complete")

# 6) 성능 평가
y_pred_train = model.predict(X_train)
y_pred_test  = model.predict(X_test)

r2_train  = r2_score(y_train, y_pred_train)
r2_test   = r2_score(y_test,  y_pred_test)
rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
rmse_test  = np.sqrt(mean_squared_error(y_test,  y_pred_test))

logger.info(f"🏅 Train  R²: {r2_train:.4f}, RMSE: {rmse_train:.4f}")
logger.info(f"🎯 Test   R²: {r2_test:.4f}, RMSE: {rmse_test:.4f}")

# 7) 모델 저장
os.makedirs(os.path.dirname(OUT_MODEL_PATH), exist_ok=True)
joblib.dump(model, OUT_MODEL_PATH)
logger.info(f"✅ Model saved to {OUT_MODEL_PATH}")

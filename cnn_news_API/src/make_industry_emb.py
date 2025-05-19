# make_industry_emb.py

import os
import json
import ast
import numpy as np
from sklearn.decomposition import PCA
import spacy
import logging

# ────── 설정 ──────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 1) 경로 설정
BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GLOVE_PATH = os.path.join(BASE_DIR, 'data', 'glove.6B.300d.txt')
KW_PATH    = os.path.join(BASE_DIR, 'data', 'industry_keywords.txt')
EMBED_OUT  = os.path.join(BASE_DIR, 'data', 'industry_emb_32d.npy')
VOCAB_OUT  = os.path.join(BASE_DIR, 'data', 'industry_vocab.json')

# 2) spaCy 모델 로드 (phrase fallback 용)
nlp = spacy.load("en_core_web_lg")

# 3) 산업 키워드 로드
with open(KW_PATH, 'r', encoding='utf-8') as f:
    src = f.read()
mod = ast.parse(src)
industry_keywords = []
for node in mod.body:
    if isinstance(node, ast.Assign):
        for targ in node.targets:
            if getattr(targ, 'id', None) == 'industry_keywords':
                industry_keywords = ast.literal_eval(node.value)
                break

if not industry_keywords:
    logger.error("Failed to load any industry_keywords")
    raise RuntimeError("industry_keywords.txt parsing failed")
logger.info(f"Loaded {len(industry_keywords)} industry keywords")

# 4) GloVe 전체 로드
glove = {}
with open(GLOVE_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split()
        word, vec = parts[0], np.array(parts[1:], dtype=np.float32)
        glove[word] = vec
logger.info(f"Loaded {len(glove)} GloVe vectors")

# 5) 구(phrase) 처리 함수
def get_phrase_vector(phrase: str):
    toks = phrase.split()
    found = [glove[t] for t in toks if t in glove]
    if found:
        return np.mean(found, axis=0)
    # spaCy fallback
    docvec = nlp(phrase).vector
    return docvec if np.linalg.norm(docvec)>0 else None

# 6) 키워드별 벡터 수집
words, vecs = [], []
for kw in industry_keywords:
    if kw in glove:
        vec = glove[kw]
    else:
        vec = get_phrase_vector(kw)
    if vec is not None:
        words.append(kw)
        vecs.append(vec)
    else:
        logger.warning(f"No embedding for keyword: {kw}")

if not words:
    logger.error("No keywords matched any embeddings")
    raise RuntimeError("No embeddings to process")

mat = np.vstack(vecs)  # shape [len(words), 300]
logger.info(f"Collected embeddings for {len(words)} keywords")

# 7) PCA 축소 (300→32)
pca = PCA(n_components=32, random_state=42)
reduced = pca.fit_transform(mat)
logger.info(f"PCA-reduced shape: {reduced.shape}")

# 8) 결과 저장
os.makedirs(os.path.dirname(EMBED_OUT), exist_ok=True)
np.save(EMBED_OUT, reduced)
with open(VOCAB_OUT, 'w', encoding='utf-8') as f:
    json.dump(words, f, ensure_ascii=False, indent=2)

logger.info(f"Saved embeddings → {EMBED_OUT}")
logger.info(f"Saved vocab      → {VOCAB_OUT}")

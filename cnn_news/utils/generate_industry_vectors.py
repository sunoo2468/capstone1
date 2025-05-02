# pipeline/generate_industry_vectors.py

import sys
import os

# 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
sys.path.append(ROOT_DIR)

import numpy as np
from utils.embedding_glove_loader import load_glove_embeddings

# 산업 키워드 리스트
industry_keywords = {
    "Software": ["software", "application", "platform", "cloud", "SaaS"],
    "Automotive": ["car", "vehicle", "transportation", "mobility", "electric"],
    "Healthcare": ["health", "medical", "hospital", "pharmaceutical", "clinic"],
    "Financials": ["bank", "finance", "insurance", "investment", "asset"],
    "Retail": ["shopping", "e-commerce", "store", "consumer", "marketplace"],
    "Semiconductors": ["semiconductor", "chip", "processor", "silicon", "fab"],
    "Telecommunications": ["communication", "mobile", "network", "broadband", "5G"],
    "Energy": ["energy", "oil", "gas", "renewable", "solar"],
    "Real Estate": ["property", "real estate", "rental", "housing", "asset"],
    "Transportation": ["logistics", "shipping", "freight", "delivery", "carrier"],
    "Food & Beverage": ["food", "beverage", "restaurant", "grocery", "nutrition"],
    "Entertainment": ["movie", "music", "entertainment", "streaming", "show"],
    "Pharmaceuticals": ["drug", "medicine", "biotech", "therapy", "vaccine"],
    "Construction": ["construction", "infrastructure", "building", "architecture", "civil"],
    "Consumer Electronics": ["electronics", "device", "gadget", "smartphone", "wearable"],
    "Utilities": ["electricity", "gas", "water", "utility", "power"],
    "Materials": ["chemical", "material", "mining", "metals", "minerals"],
    "Insurance": ["insurance", "coverage", "risk", "policy", "claim"],
    "Biotechnology": ["biotech", "genome", "therapy", "research", "innovation"],
    "Aerospace & Defense": ["aerospace", "defense", "military", "aviation", "missile"],
    "Media": ["media", "broadcasting", "publishing", "news", "journalism"],
    "Hospitality": ["hotel", "travel", "tourism", "accommodation", "leisure"]
}

# 경로 설정
save_dir = os.path.join(DATA_DIR, "industry_vectors")
os.makedirs(save_dir, exist_ok=True)

# GloVe 로딩
glove_path = os.path.join(DATA_DIR, "collect_company", "glove.6B.300d.txt")
glove_embeddings = load_glove_embeddings(glove_path)

def build_industry_vector(keywords, glove_embeddings):
    vectors = [glove_embeddings[word] for word in keywords if word in glove_embeddings]
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return None

# 산업별 벡터 생성
for industry, keywords in industry_keywords.items():
    vector = build_industry_vector(keywords, glove_embeddings)
    if vector is not None:
        save_path = os.path.join(save_dir, f"{industry}.npy")
        np.save(save_path, vector)
        print(f"✅ {industry} 산업 벡터 저장 완료")
    else:
        print(f"❌ {industry} 산업 벡터 생성 실패")

# utils/company_vector_builder.py

import numpy as np

def build_company_vector(keywords, glove_embeddings):
    """
    키워드 리스트를 GloVe 임베딩 평균해서 기업 벡터 생성
    """
    vectors = [glove_embeddings[word] for word in keywords if word in glove_embeddings]
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return None

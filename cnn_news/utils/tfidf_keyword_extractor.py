# utils/tfidf_keyword_extractor.py

from sklearn.feature_extraction.text import TfidfVectorizer

def extract_top_keywords(text, top_k=10):
    """
    텍스트로부터 TF-IDF 기반 상위 top_k개 키워드 추출
    """
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform([text])
    scores = tfidf_matrix.toarray()[0]
    features = vectorizer.get_feature_names_out()
    top_indices = scores.argsort()[::-1][:top_k]
    return [features[i] for i in top_indices]

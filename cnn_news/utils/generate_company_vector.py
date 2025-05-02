# utils/generate_company_vector.py

from utils.sec_cik_fetcher import get_cik
from utils.sec_10k_url_fetcher import get_10k_filing_urls
from utils.sec_10k_text_extractor import extract_text_from_url
from utils.tfidf_keyword_extractor import extract_top_keywords
from utils.company_vector_builder import build_company_vector

def generate_company_vector_from_ticker(ticker, glove_embeddings):
    """
    티커를 입력받아 기업 임베딩 벡터를 생성하는 최종 통합 함수
    """
    cik = get_cik(ticker)
    if not cik:
        print(f"❌ {ticker}: CIK를 찾을 수 없음")
        return None

    filing_urls = get_10k_filing_urls(cik)
    if not filing_urls:
        print(f"❌ {ticker}: 10-K 파일 URL을 찾을 수 없음")
        return None

    text = extract_text_from_url(filing_urls[0])
    keywords = extract_top_keywords(text, top_k=10)

    # 산업 관련 3개 키워드만 골라
    top_keywords = [word for word in keywords if word in glove_embeddings][:3]

    company_vector = build_company_vector(top_keywords, glove_embeddings)
    return company_vector

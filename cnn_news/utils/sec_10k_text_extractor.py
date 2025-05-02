# utils/sec_10k_text_extractor.py

import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    """
    10-K 문서 URL에서 본문 텍스트 추출
    """
    headers = {'User-Agent': 'your_email@example.com'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text

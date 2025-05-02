# utils/sec_cik_fetcher.py

import requests

def get_cik(ticker):
    """
    Ticker를 받아 SEC 등록된 CIK 코드로 변환
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {'User-Agent': 'your_email@example.com'}
    data = requests.get(url, headers=headers).json()
    for k, v in data.items():
        if v['ticker'].lower() == ticker.lower():
            return str(v['cik_str']).zfill(10)
    return None

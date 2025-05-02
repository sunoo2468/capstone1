# utils/sec_10k_url_fetcher.py

import requests

def get_10k_filing_urls(cik):
    """
    CIK를 입력받아 최근 제출된 10-K 문서 URL 가져오기
    """
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {'User-Agent': 'your_email@example.com'}
    data = requests.get(url, headers=headers).json()
    urls = []
    for filing in data['filings']['recent']['form']:
        if filing == "10-K":
            index = data['filings']['recent']['form'].index(filing)
            accession = data['filings']['recent']['accessionNumber'][index].replace("-", "")
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
            doc_data = requests.get(doc_url, headers=headers).json()
            for file in doc_data['directory']['item']:
                if file['name'].endswith(".htm") or file['name'].endswith(".txt"):
                    urls.append(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{file['name']}")
            break
    return urls

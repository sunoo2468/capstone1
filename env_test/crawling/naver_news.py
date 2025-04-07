import requests
from bs4 import BeautifulSoup
import json
import os

query = "인공지능"
url = f"https://search.naver.com/search.naver?where=news&query={query}"

headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

articles = soup.select("a.news_tit")
titles = []

for a in articles:
    title = a["title"].strip()
    if title:
        titles.append(title)

# 저장 경로: ../data/naver_titles.json
save_path = os.path.join("..", "data", "naver_titles.json")
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(titles, f, ensure_ascii=False, indent=2)

print(f"총 {len(titles)}개 제목 저장 완료!")

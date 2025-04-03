import requests
from bs4 import BeautifulSoup

query = "인공지능"
url = f"https://search.naver.com/search.naver?where=news&query={query}"

headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

articles = soup.select("a.news_tit")
for a in articles:
    print("제목:", a["title"])
    print("링크:", a["href"])
    print("-" * 50)
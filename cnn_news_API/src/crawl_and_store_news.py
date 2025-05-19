# crawl_and_store_news.py

import os
import time
import logging
import requests
import pandas as pd
import nltk
import spacy
import ast
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
from dotenv import load_dotenv

# ────── 설정 ──────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 1) 환경 변수 로드
load_dotenv()
API_KEY = os.getenv('NEWSAPI_KEY')
if not API_KEY:
    logger.error("NEWSAPI_KEY not found in environment variables")
    raise ValueError("NEWSAPI_KEY not found")

# 2) 감성 분석 & NER 모델 초기화
nltk.download('vader_lexicon', quiet=True)
vader = SentimentIntensityAnalyzer()
nlp = spacy.load("en_core_web_lg")

# 3) 날짜 범위 설정
today     = datetime.today()
from_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
to_date   = today.strftime('%Y-%m-%d')

# 4) NASDAQ 매핑
BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
nasdaq_csv  = os.path.join(BASE_DIR, 'data', 'nasdaq_screener_1744184912302.csv')
ticker_name_map = {}
if os.path.exists(nasdaq_csv):
    df_nasdaq = pd.read_csv(nasdaq_csv)
    required_cols = {"Symbol","Name","Market Cap","Sector"}
    missing = required_cols - set(df_nasdaq.columns)
    if missing:
        logger.error(f"Missing columns in NASDAQ CSV: {missing}")
        raise RuntimeError(f"NASDAQ CSV missing: {missing}")
    mask = (
        (df_nasdaq["Market Cap"] > 0) &
        df_nasdaq["Sector"].notnull() &
        ~df_nasdaq["Name"].str.contains("Units|Rights|Warrant|Preferred|Depositary|Series", case=False)
    )
    df_clean = df_nasdaq[mask].drop_duplicates(subset="Symbol")
    df_clean["Symbol"] = df_clean["Symbol"].str.lower().str.strip()
    df_clean["Name"]   = df_clean["Name"].str.strip()
    ticker_name_map    = dict(zip(df_clean["Symbol"], df_clean["Name"]))
    logger.info(f"Loaded {len(ticker_name_map)} ticker-name mappings")
else:
    logger.warning("NASDAQ mapping CSV not found; continuing without ticker mapping")

# 5) 산업 키워드 로드
kw_path = os.path.join(BASE_DIR, 'data', 'industry_keywords.txt')
with open(kw_path, 'r', encoding='utf-8') as f:
    contents = f.read()
mod = ast.parse(contents)
industry_keywords = []
for node in mod.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if getattr(target, 'id', None) == 'industry_keywords':
                industry_keywords = ast.literal_eval(node.value)
                break
if not industry_keywords:
    logger.error("No industry_keywords loaded")
    raise RuntimeError("industry_keywords.txt parsing failed")
logger.info(f"Loaded {len(industry_keywords)} industry keywords")

# 6) 크롤링 파라미터
API_URL   = "https://newsapi.org/v2/everything"
params    = {
    'q':        'nasdaq OR stock OR technology OR innovation',
    'from':     from_date,
    'to':       to_date,
    'language': 'en',
    'pageSize': 100,
    'domains':  'cnn.com',
    'apiKey':   API_KEY,
    'sortBy':   'publishedAt'
}
MAX_PAGES = 1  # 무료 플랜 최대 100건만 수집

# 7) 뉴스 수집
articles = []
for page in range(1, MAX_PAGES + 1):
    params['page'] = page
    res = requests.get(API_URL, params=params, headers={'User-Agent':'Mozilla/5.0'})
    try:
        data = res.json()
    except ValueError:
        logger.error("Invalid JSON response from NewsAPI")
        break

    if res.status_code != 200:
        code = data.get('code','')
        if code == 'maximumResultsReached':
            logger.warning("Reached free-plan limit (100 articles). Stopping.")
        else:
            logger.error(f"API error {res.status_code}: {data.get('message','')}")
        break

    articles_batch = data.get('articles')
    if not isinstance(articles_batch, list):
        logger.error("Unexpected API response structure")
        break
    if not articles_batch:
        break

    for art in articles_batch:
        full = ' '.join(filter(None, [
            art.get('title'),
            art.get('description'),
            art.get('content')
        ]))
        articles.append({
            'title':        art.get('title',''),
            'description':  art.get('description',''),
            'content':      art.get('content',''),
            'url':          art.get('url',''),
            'published_at': art.get('publishedAt',''),
            'full_text':    full
        })
    time.sleep(1)

logger.info(f"Crawled total articles: {len(articles)}")

# 8) DataFrame 생성 & 체크
df = pd.DataFrame(articles)
if df.empty:
    logger.error("No articles collected; exiting")
    raise RuntimeError("No data to process")

# 9) 감성·키워드 추출 함수
def extract_positive_orgs(text, max_orgs=3):
    if not isinstance(text, str):
        return []
    if vader.polarity_scores(text)['compound'] <= 0:
        return []
    doc = nlp(text)
    orgs = [ent.text.lower() for ent in doc.ents if ent.label_=='ORG']
    found, added = [], set()
    for name in orgs:
        for sym, nm in ticker_name_map.items():
            if name in nm.lower() or nm.lower() in name:
                if sym and sym not in added:
                    found.append(sym); added.add(sym)
                break
        if len(found) >= max_orgs:
            break
    return found

def extract_industry_keywords(text):
    txt = text.lower() if isinstance(text, str) else ""
    return [kw for kw in industry_keywords if kw in txt]

# 10) 필터링 & 정제
df['positive_orgs']  = df['full_text'].apply(extract_positive_orgs)
df['industry_keys']  = df['full_text'].apply(extract_industry_keywords)
df_f = df[(df['positive_orgs'].str.len()>0) | (df['industry_keys'].str.len()>0)].copy()

for col in ['positive_orgs','industry_keys']:
    df_f[col] = (
        df_f[col]
        .apply(lambda lst: [s for s in lst if s])
        .apply(lambda lst: ','.join(lst))
    )

# 11) SQLite DB 저장
db_path = os.path.join(BASE_DIR, 'data', 'cnn_news.db')
engine  = create_engine(f"sqlite:///{db_path}")
df_f.to_sql('cnn_positive_news', engine, if_exists='replace', index=False)
logger.info(f"Stored {len(df_f)} positive articles in `cnn_positive_news` table")

# 12) 통계 출력
org_counts      = Counter(df_f['positive_orgs'].str.split(',').sum())
industry_counts = Counter(df_f['industry_keys'].str.split(',').sum())
org_counts.pop('', None)
industry_counts.pop('', None)

logger.info(f"Top 기업 키워드: {org_counts.most_common(10)}")
logger.info(f"Top 산업 키워드: {industry_counts.most_common(10)}")

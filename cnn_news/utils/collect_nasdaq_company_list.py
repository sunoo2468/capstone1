# utils/collect_nasdaq_from_ftp.py

import pandas as pd
import os

# 저장 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "collect_company")
os.makedirs(DATA_DIR, exist_ok=True)

SAVE_PATH = os.path.join(DATA_DIR, "nasdaq_company_list.csv")

# 공식 NASDAQ FTP 주소
url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"

# 데이터 수집 및 정제
df = pd.read_csv(url, sep="|")
df = df[df["Test Issue"] == "N"]  # 테스트 종목 제외
df = df[["Symbol", "Security Name"]].copy()
df.columns = ["티커", "기업명"]
df["국가"] = "United States"

# 저장
df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")
print(f"✅ NASDAQ 기업 리스트 저장 완료 → {SAVE_PATH}")
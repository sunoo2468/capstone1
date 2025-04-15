# utils/collect_nasdaq_company_list_2.py

from yahoo_fin import stock_info as si
from yahooquery import Ticker
import pandas as pd
import os
import time

# 저장 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "collect_company")
os.makedirs(DATA_DIR, exist_ok=True)

SAVE_PATH = os.path.join(DATA_DIR, "nasdaq_company_list_2.csv")

# 1. NASDAQ 전체 티커 리스트 자동 수집
def get_nasdaq_tickers(limit=300):
    tickers = si.tickers_nasdaq()
    print(f"✅ NASDAQ 티커 {len(tickers)}개 중 {limit}개 사용")
    return tickers[:limit]

# 2. 티커별 상세 정보 수집 함수
def fetch_nasdaq_info(tickers: list) -> pd.DataFrame:
    all_data = []

    for i, symbol in enumerate(tickers, 1):
        try:
            ticker = Ticker(symbol)
            summary = ticker.asset_profile.get(symbol, {})
            price_info = ticker.price.get(symbol, {})

            all_data.append({
                "티커": symbol,
                "기업명": price_info.get("longName", "N/A"),
                "산업군": summary.get("industry", "Unknown"),
                "국가": summary.get("country", "USA"),
                "시가총액": price_info.get("marketCap", "N/A")
            })

            print(f"[{i}/{len(tickers)}] ✅ {symbol} 수집 완료")
            time.sleep(0.5)  # 과도한 요청 방지

        except Exception as e:
            print(f"[{i}/{len(tickers)}] ⚠️ {symbol} 수집 실패: {e}")
            continue

    df = pd.DataFrame(all_data)
    df.to_csv(SAVE_PATH, index=False, encoding='utf-8-sig')
    print(f"\n✅ NASDAQ 기업 {len(df)}개 저장 완료 → {SAVE_PATH}")
    return df

# 실행
if __name__ == "__main__":
    tickers = get_nasdaq_tickers(limit=300)
    fetch_nasdaq_info(tickers)
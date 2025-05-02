# utils/collect_nasdaq_company_list_yf.py

import pandas as pd
import yfinance as yf
import os, json, time

# 디렉토리 설정
ROOT_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COLLECT_COMPANY_DIR = os.path.join(ROOT_DATA_DIR, "collect_company")
MAPPING_DIR = os.path.join(ROOT_DATA_DIR, "mapping")
os.makedirs(COLLECT_COMPANY_DIR, exist_ok=True)
os.makedirs(MAPPING_DIR, exist_ok=True)

def download_nasdaq_ticker_list():
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")
    df = df[df["Symbol"].notna() & df["Test Issue"] != "Y"]
    tickers = df["Symbol"].tolist()
    print(f"✅ NASDAQ 티커 {len(tickers)}개 로드됨")
    return tickers

def save_all_in_batches(tickers, batch_size=500):
    records = []
    failed = []

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        print(f"\n📦 Batch {i//batch_size+1}: {len(batch)}개 수집 중...")

        for tkr in batch:
            try:
                info = yf.Ticker(tkr).info
                name = info.get("shortName", tkr)
                records.append({"기업명": name, "Ticker": tkr})
                time.sleep(0.2)
            except Exception as e:
                print(f" {tkr} 실패: {e}")
                failed.append(tkr)

    # 마지막에 한 번만 저장
    json_path = os.path.join(MAPPING_DIR, "ticker_list.json")
    csv_path = os.path.join(COLLECT_COMPANY_DIR, "final_company_list.csv")
    fail_path = os.path.join(COLLECT_COMPANY_DIR, "failed_tickers.txt")

    with open(json_path, "w") as f:
        json.dump([r["Ticker"] for r in records], f)

    pd.DataFrame(records).to_csv(csv_path, index=False)

    with open(fail_path, "w") as f:
        f.write("\n".join(failed))

    print(f"\n 최종 저장 완료: {len(records)}개 기업 → {csv_path}")
    print(f" 실패한 티커: {len(failed)}개 → {fail_path}")

if __name__ == "__main__":
    tickers = download_nasdaq_ticker_list()
    save_all_in_batches(tickers, batch_size=500)

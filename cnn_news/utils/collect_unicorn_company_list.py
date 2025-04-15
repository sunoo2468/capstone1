# utils/clean_unicorn_excel.py

import pandas as pd
import os

# 저장 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "collect_company")
os.makedirs(DATA_DIR, exist_ok=True)

# 원본 엑셀 파일 경로
EXCEL_PATH = os.path.join(ROOT_DIR, "data", "CB-Insights_Global-Unicorn-Club_2025.xlsx")
SAVE_PATH = os.path.join(DATA_DIR, "unicorn_company_list.csv")

# 1. 엑셀 파일 로드 (3번째 줄을 헤더로 인식)
df = pd.read_excel(EXCEL_PATH, sheet_name='Unicorns', header=2)

# 2. 컬럼명만 한글로 바꾸기 (데이터 그대로)
df = df.rename(columns={
    "Company": "기업명",
    "Valuation ($B)": "가치평가(억$)",
    "Date Joined": "유니콘 등록일",
    "Country": "국가",
    "City": "도시",
    "Industry": "산업군",
    "Select Investors": "투자자"
})

# 3. '기업명'이 NaN인 행 제거 (푸터 제거)
df = df[df["기업명"].notna()]

# 4. 저장
df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")
print(f"✅ 유니콘 기업 {len(df)}개 저장 완료 → {SAVE_PATH}")
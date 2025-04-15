# utils/generate_company_synonyms.py

import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

# .env에서 API 키 로딩
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMPANY_CSV_PATH = os.path.join(ROOT_DIR, "data", "collect_company", "final_company_list.csv")
SAVE_PATH = os.path.join(ROOT_DIR, "data", "collect_company", "company_synonyms.csv")

# 기업 리스트 로딩
companies = pd.read_csv(COMPANY_CSV_PATH)["기업명"].dropna().unique().tolist()

# 프롬프트 템플릿
def build_prompt(company_name):
    return f"""
다음은 실제 기업명입니다. 뉴스, 커뮤니티, SNS 등에서 이 기업이 자주 어떻게 불리는지 3~5개의 표현(동의어, 줄임말, 일반적인 언급 등)을 알려주세요. 

기업명: {company_name}
동의어 리스트:
"""

# GPT 호출 함수 (OpenAI v1.x 방식)
def get_synonyms(company_name):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 뉴스 기반 키워드 전문가입니다."},
                {"role": "user", "content": build_prompt(company_name)}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"

# 전체 기업 실행
results = []
for company in companies:
    print(f"🔍 Generating for: {company}")
    synonyms = get_synonyms(company)
    results.append({"기업명": company, "표현": synonyms})

# 저장
syn_df = pd.DataFrame(results)
syn_df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")
print(f"✅ 저장 완료 → {SAVE_PATH}")
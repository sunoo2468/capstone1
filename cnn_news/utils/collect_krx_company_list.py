# utils/collect_krx_company_list.py

import os
import requests
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from dotenv import load_dotenv

# 루트 디렉토리와 저장 폴더 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "collect_company")
os.makedirs(DATA_DIR, exist_ok=True)

# .env 파일에서 API 키 불러오기
load_dotenv()
API_KEY = os.getenv("DART_API_KEY")

# 1. corpCode.zip 다운로드 함수
def fetch_krx_company_list():
    url = "https://opendart.fss.or.kr/api/corpCode.xml"
    params = {"crtfc_key": API_KEY}

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        zip_path = os.path.join(DATA_DIR, "corpCode.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        print("✅ KRX 기업 코드 ZIP 다운로드 완료!")
    else:
        print("❌ 오류 발생:", response.text)
        raise Exception("OpenDART ZIP 다운로드 실패")

# 2. ZIP 압축 해제 및 XML 파싱 → CSV 저장
def parse_krx_corp_code(zip_path: str = None, save_path: str = None) -> pd.DataFrame:
    zip_path = zip_path or os.path.join(DATA_DIR, "corpCode.zip")
    save_path = save_path or os.path.join(DATA_DIR, "krx_company_list.csv")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)

    xml_path = os.path.join(DATA_DIR, "CORPCODE.xml")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    rows = []
    for child in root.findall("list"):
        corp_code = child.find("corp_code").text
        corp_name = child.find("corp_name").text
        stock_code = child.find("stock_code").text
        modify_date = child.find("modify_date").text

        if stock_code.strip():  # 종목코드 있는 경우만
            rows.append({
                "corp_code": corp_code,
                "기업명": corp_name,
                "종목코드": stock_code,
                "수정일": modify_date,
                "국가": "Korea"
            })

    df = pd.DataFrame(rows)
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"✅ {len(df)}개 기업 저장 완료 → {save_path}")
    return df

# 전체 실행
if __name__ == "__main__":
    fetch_krx_company_list()
    parse_krx_corp_code()
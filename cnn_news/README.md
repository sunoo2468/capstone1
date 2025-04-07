# CNN 뉴스 기반 산업/기업 키워드 추출 시스템

## 구조
- `extraction/` : 키워드 추출, 감성 분석
- `embedding/` : 임베딩 처리
- `pipeline/` : 전체 파이프라인
- `utils/` : 전처리 함수

## 가상환경 생성
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 📖 README

```markdown
# CNN-News Embedding 기반 산업·기업 유망도 예측

## 개요
CNN 뉴스 크롤링 → 산업·기업 임베딩 생성 → 대조학습 개선 → 유망도 예측(Ridge)  
“임베딩 벡터를 인풋으로 활용”하는 전 과정을 자동화한 파이프라인입니다.

## 환경 설정
1. Python 3.8+  
2. `pip install -r requirements.txt`  
   - 주요: `requests`, `pandas`, `nltk`, `spacy`, `sqlalchemy`, `scikit-learn`, `torch`, `joblib`, `python-dotenv`

3. spaCy 모델 다운로드  
```
python -m spacy download en\_core\_web\_lg
```

4. `.env` 파일에 NewsAPI 키 설정  
```
NEWSAPI\_KEY=YOUR\_KEY\_HERE
````

## 사용법

### 1. 뉴스 수집
```bash
python src/crawl_and_store_news.py
````

* 수집된 긍정 기사(‘cnn\_positive\_news’ 테이블)가 `data/cnn_news.db`에 저장됩니다.

### 2. 산업 임베딩 생성

```bash
python src/make_industry_emb.py
```

* GloVe → (PCA) → `data/industry_emb_32d.npy`, `data/industry_vocab.json` 생성.

### 3. 유망도 레이블 산출

```bash
python src/make_promise_labels.py
```

* `data/industry_promise.csv` 생성 (freq, positive\_rate → promise\_label).

### 4. 유망도 예측기 학습

```bash
python src/train_promise_predictor.py
```

* 산업 임베딩 → 유망도 예측 모델(`models/promise_predictor.pkl`) 저장.

### 5. Contrastive 학습

```bash
python src/train_contrastive.py
```

* GloVe→PCA 64d → 뉴스 문장 임베딩 → `models/projector.pth` 저장.

### 6. 기업 스코어링

```bash
python src/score_companies.py
```

* `data/nasdaq_screener_*.csv` 기반으로 기업 임베딩 생성 후
  모델 예측 → `results/company_promise_score.csv` 출력.

## 구조

```
src/
├─ crawl_and_store_news.py
├─ make_industry_emb.py
├─ make_promise_labels.py
├─ train_promise_predictor.py
├─ train_contrastive.py
└─ score_companies.py
data/
models/
results/
.env
```

## 문의 및 기여

* Issues/PR 환영합니다.
* 개선 아이디어: 산업 유망도 외부 지표 도입, 모델 동시 학습, 시각화 대시보드 등

---

```

from transformers import pipeline

# 감성 분석 파이프라인 (huggingface model 사용)
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text):
    """
    주어진 텍스트에 대해 감성 분석 결과 리턴
    예: {'label': 'POSITIVE', 'score': 0.998}
    """
    result = sentiment_pipeline(text[:512])  # max token 제한
    return result[0] if result else {"label": "NEUTRAL", "score": 0.0}

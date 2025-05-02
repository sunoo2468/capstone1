# utils/embedding_glove_loader.py

def load_glove_embeddings(glove_path):
    """
    Glove.6B.300d.txt 파일을 로드하여 단어 → 벡터 딕셔너리 생성

    Args:
        glove_path (str): GloVe 파일 경로

    Returns:
        dict: {단어: 벡터 리스트}
    """
    embeddings = {}
    with open(glove_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            word = parts[0]
            vector = list(map(float, parts[1:]))
            embeddings[word] = vector
    print(f" GloVe 단어 {len(embeddings)}개 로드 완료")
    return embeddings

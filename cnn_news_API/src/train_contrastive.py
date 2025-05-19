# train_contrastive.py

import os
import json
import numpy as np
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader
from sqlalchemy import create_engine
import pandas as pd
from sklearn.decomposition import PCA

# 1) 경로 설정
BASE_DIR             = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GLOVE_TXT_PATH       = os.path.join(BASE_DIR, 'data', 'glove.6B.300d.txt')
GLOVE_PCA_EMBED_PATH = os.path.join(BASE_DIR, 'data', 'glove_pca_64d.npy')
GLOVE_PCA_VOCAB_PATH = os.path.join(BASE_DIR, 'data', 'glove_pca_vocab.json')
DB_PATH              = os.path.join(BASE_DIR, 'data', 'cnn_news.db')
OUT_MODEL_PATH       = os.path.join(BASE_DIR, 'models', 'projector.pth')

# 2) GloVe→PCA preprocessing if needed
if not os.path.exists(GLOVE_PCA_EMBED_PATH):
    print("🏗 Generating Glove-PCA embeddings (64d)…")
    words, vecs = [], []
    with open(GLOVE_TXT_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            vals = line.split()
            words.append(vals[0])
            vecs.append(np.array(vals[1:], dtype=np.float32))
    mat = np.vstack(vecs)
    pca = PCA(n_components=64)
    reduced = pca.fit_transform(mat)
    os.makedirs(os.path.dirname(GLOVE_PCA_EMBED_PATH), exist_ok=True)
    np.save(GLOVE_PCA_EMBED_PATH, reduced)
    with open(GLOVE_PCA_VOCAB_PATH, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)
    print(f"✅ Saved PCA embeddings → {GLOVE_PCA_EMBED_PATH}")

# 3) Load PCA'd GloVe
vectors = np.load(GLOVE_PCA_EMBED_PATH)   # shape (V, D)
with open(GLOVE_PCA_VOCAB_PATH, 'r', encoding='utf-8') as f:
    vocab = json.load(f)                 # length V
glove_pca = dict(zip(vocab, vectors))

# 4) Load CNN news and vectorize
engine = create_engine(f'sqlite:///{DB_PATH}')
df = pd.read_sql_table('cnn_positive_news', engine)
texts = df['full_text'].dropna().tolist()

def get_text_vector(text):
    toks = text.split()
    vs = [glove_pca[t.lower()] for t in toks if t.lower() in glove_pca]
    return np.mean(vs, axis=0) if vs else None

# build sample matrix
sample_list = [get_text_vector(t) for t in texts]
sample_list = [v for v in sample_list if v is not None]
samples_np  = np.stack(sample_list)  # shape (N, D)
print(f"🧪 Total contrastive samples: {len(samples_np)}")

# 5) Dataset & DataLoader
class ContrastiveDataset(Dataset):
    def __init__(self, array: np.ndarray):
        # array: NumPy array shape (N, D)
        self.vecs = torch.from_numpy(array.astype(np.float32))
    def __len__(self):
        # leave at least 2 ahead for (pos, neg)
        return self.vecs.size(0) - 2
    def __getitem__(self, idx):
        # return (anchor, positive, negative)
        return self.vecs[idx], self.vecs[idx+1], self.vecs[idx+2]

loader = DataLoader(ContrastiveDataset(samples_np), batch_size=32, shuffle=True)

# 6) Model & optimizer
D = samples_np.shape[1]  # embedding dimension (should be 64)
class ContrastiveProjector(nn.Module):
    def __init__(self, dim=D):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, dim),
            nn.ReLU(),
            nn.Linear(dim, dim)
        )
    def forward(self, x):
        return self.net(x)

device    = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model     = ContrastiveProjector(dim=D).to(device)
optimizer = Adam(model.parameters(), lr=1e-3)
loss_fn   = nn.CosineEmbeddingLoss()

# 7) Training loop
epochs = 10
for epoch in range(1, epochs+1):
    total_loss = 0.0
    for a, p, n in loader:
        a, p, n = a.to(device), p.to(device), n.to(device)
        za, zp, zn = model(a), model(p), model(n)
        y_pos = torch.ones(za.size(0), device=device)
        y_neg = -torch.ones(za.size(0), device=device)
        loss = loss_fn(za, zp, y_pos) + loss_fn(za, zn, y_neg)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch}/{epochs}, Loss: {total_loss/len(loader):.4f}")

# 8) Save projector
os.makedirs(os.path.dirname(OUT_MODEL_PATH), exist_ok=True)
torch.save(model.state_dict(), OUT_MODEL_PATH)
print(f"✅ Contrastive projector saved → {OUT_MODEL_PATH}")

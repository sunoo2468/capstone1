# utils/compress_company_vectors.py
"""
company_vectors/*.npy → embeddings/company_vectors.json
실행 예)  python -m utils.compress_company_vectors
"""
import os, glob, json, numpy as np, pathlib, sys
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
VEC_DIR  = ROOT_DIR / "data" / "company_vectors"
OUT_F    = ROOT_DIR / "data" / "embeddings" / "company_vectors.json"
OUT_F.parent.mkdir(parents=True, exist_ok=True)

vectors = {pathlib.Path(p).stem: np.load(p).astype(float).tolist()
           for p in glob.glob(str(VEC_DIR / "*.npy"))}
with open(OUT_F, "w") as f: json.dump(vectors, f)
print(f" {len(vectors)} vectors → {OUT_F}")

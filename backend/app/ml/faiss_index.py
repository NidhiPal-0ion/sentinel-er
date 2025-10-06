# backend/app/ml/faiss_index.py
import faiss
import numpy as np
import pandas as pd
import joblib

# Load embeddings
df = pd.read_csv("data/face_embeddings.csv")
embeddings = np.vstack(df.embedding.apply(lambda x: np.array(eval(x))))  # convert string '[0.1,...]' to np.array
face_ids = df.face_id.values

dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)
joblib.dump((index, face_ids), "models/faiss_index.pkl")

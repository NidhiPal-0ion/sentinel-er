# import pandas as pd
# from rapidfuzz import fuzz
# import faiss
# import numpy as np
# from sqlalchemy import create_engine
# import os

# # ----------------- Database Config -----------------
# DB_USER = "admin"
# DB_PASSWORD = "admin"
# DB_HOST = "localhost"
# DB_PORT = "5432"
# DB_NAME = "sentinel"

# DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# engine = create_engine(DATABASE_URL)

# # ----------------- Test Entity Resolution -----------------
# def test_entity_resolution():
#     profiles = pd.read_sql("SELECT * FROM profiles", engine)
#     embeddings = pd.read_sql("SELECT * FROM face_embeddings", engine)

#     # Simple fuzzy match test
#     query_name = "Amit Sharma"
#     matches = []
#     for _, row in profiles.iterrows():
#         score = fuzz.ratio(query_name.lower(), row["name"].lower())
#         if score > 80:
#             matches.append((row["id"], row["name"], score))

#     print("Fuzzy Matches:", matches)
#     print("Embeddings Count:", len(embeddings))

# # ----------------- EntityResolver Class -----------------
# class EntityResolver:
#     def __init__(self, profiles_df, embeddings_df):
#         self.profiles = profiles_df
#         self.embeddings = embeddings_df
#         self.index = self._build_faiss_index()

#     def _build_faiss_index(self):
#         vectors = np.array(self.embeddings["embedding"].tolist()).astype("float32")
#         index = faiss.IndexFlatL2(vectors.shape[1])
#         index.add(vectors)
#         return index

#     def resolve_by_face(self, query_vector, top_k=3):
#         query = np.array([query_vector]).astype("float32")
#         D, I = self.index.search(query, top_k)
#         results = self.embeddings.iloc[I[0]]
#         return results

#     def fuzzy_match_name(self, name, threshold=80):
#         matches = []
#         for _, row in self.profiles.iterrows():
#             score = fuzz.ratio(name.lower(), row["name"].lower())
#             if score > threshold:
#                 matches.append((row["id"], row["name"], score))
#         return matches

# # ----------------- Main -----------------
# if __name__ == "__main__":
#     test_entity_resolution()

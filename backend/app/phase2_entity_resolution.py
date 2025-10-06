import pandas as pd
import numpy as np
import ast
import re
from sqlalchemy import create_engine
from rapidfuzz import fuzz, process
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# DATABASE CONFIG
# -----------------------------
DATABASE_URL = "postgresql://admin:admin@localhost:5432/sentinel"
engine = create_engine(DATABASE_URL)

# -----------------------------
# DATA CLEANING FUNCTIONS
# -----------------------------
def normalize_text(x):
    if pd.isna(x):
        return None
    return re.sub(r'\s+', ' ', str(x).strip().lower())

def validate_timestamp(ts):
    if pd.isna(ts):
        return None
    try:
        return pd.to_datetime(ts)
    except:
        return None

# -----------------------------
# LOAD TABLES
# -----------------------------
def load_table(table_name):
    print(f"🔹 Loading table {table_name}...")
    df = pd.read_sql(table_name, engine)
    return df

# -----------------------------
# EMBEDDING PARSING
# -----------------------------
def parse_embedding(x):
    try:
        if isinstance(x, str):
            x = ast.literal_eval(x)
        arr = np.array(x, dtype=float)
        return arr
    except:
        return None

# -----------------------------
# FUZZY MATCH
# -----------------------------
def match_fuzzy(df, key_column, threshold=85):
    matches = []
    values = df[key_column].dropna().unique()
    for val in values:
        result = process.extractOne(val, values, scorer=fuzz.token_sort_ratio)
        if result:
            potential, score, _ = result
            if score >= threshold and val != potential:
                idx1 = df[df[key_column] == val].index[0]
                idx2 = df[df[key_column] == potential].index[0]
                matches.append((idx1, idx2, score))
    return matches

# -----------------------------
# EMBEDDING SIMILARITY
# -----------------------------
def embedding_similarity(df_embeddings, threshold=0.85):
    df_embeddings['embedding_list'] = df_embeddings['embedding'].apply(parse_embedding)
    df_embeddings = df_embeddings[df_embeddings['embedding_list'].notna()]

    if df_embeddings.empty:
        return []

    # Ensure all embeddings have same length
    lengths = df_embeddings['embedding_list'].apply(lambda x: x.shape[0])
    expected_length = lengths.mode()[0]
    df_embeddings = df_embeddings[lengths == expected_length]

    if df_embeddings.empty:
        return []

    embeddings = np.stack(df_embeddings['embedding_list'].values)
    sim_matrix = cosine_similarity(embeddings)

    pairs = []
    for i in range(len(sim_matrix)):
        for j in range(i + 1, len(sim_matrix)):
            if sim_matrix[i, j] >= threshold:
                pairs.append((df_embeddings.iloc[i].get('face_id'), df_embeddings.iloc[j].get('face_id'), sim_matrix[i, j]))
    return pairs

# -----------------------------
# EXACT MATCH
# -----------------------------
def match_exact(df1, df2, column):
    if column not in df1.columns or column not in df2.columns:
        return pd.DataFrame()
    return df1.merge(df2[[column]].drop_duplicates(), on=column, how='left', suffixes=('', '_right'))

# -----------------------------
# MAIN ENTITY RESOLUTION
# -----------------------------
def consolidate_entities():
    # Load cleaned tables
    profiles = load_table('profiles_cleaned')
    face_embeddings = load_table('face_embeddings_cleaned')
    wifi_logs = load_table('wifi_associations_logs_cleaned')
    card_swipes = load_table('campus_card_swipes_cleaned')

    entities = profiles.copy()

    # Exact match: student_id
    print("🔹 Linking exact student_id matches...")
    if 'student_id' in face_embeddings.columns:
        entities = entities.merge(face_embeddings[['student_id', 'face_id']], on='student_id', how='left')

    # Exact match: device_hash
    print("🔹 Linking exact device_hash matches...")
    entities = match_exact(entities, wifi_logs, 'device_hash')

    # Fuzzy name match
    print("🔹 Performing fuzzy name matching...")
    fuzzy_matches = match_fuzzy(entities, 'name', threshold=85)
    print(f"✅ Found {len(fuzzy_matches)} fuzzy name matches")

    # Embedding similarity
    print("🔹 Calculating face embedding similarities...")
    embedding_pairs = embedding_similarity(face_embeddings, threshold=0.85)
    print(f"✅ Found {len(embedding_pairs)} embedding-based matches")

    # Consolidate final entities safely
    final_cols = ['student_id', 'staff_id', 'name', 'email', 'device_hash', 'face_id']
    for col in final_cols:
        if col not in entities.columns:
            entities[col] = None

    entities_resolved = entities[final_cols].drop_duplicates()

    # Save to Postgres
    print("🔹 Saving consolidated entity table...")
    entities_resolved.to_sql('entities_resolved', engine, if_exists='replace', index=False)
    print("🎉 Phase 2 complete! Data cleaning + entity resolution done.")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    consolidate_entities()

# # # #!/usr/bin/env python3
# # import os
# # import joblib
# # import pandas as pd
# # import psycopg2
# # from psycopg2.extras import RealDictCursor
# # from sklearn.preprocessing import LabelEncoder
# # from sklearn.ensemble import RandomForestClassifier

# # # -----------------------------
# # # PostgreSQL connection details
# # # -----------------------------
# # PG = {
# #     "dbname": "sentinel",
# #     "user": "admin",
# #     "password": "admin",
# #     "host": "localhost",
# #     "port": 5432
# # }

# # # -----------------------------
# # # 1️⃣ Load cleaned event data from v_all_events_clean
# # # -----------------------------
# # conn = psycopg2.connect(**PG, cursor_factory=RealDictCursor)
# # query = """
# # SELECT student_id, loc AS last_location, 
# #        LEAD(loc) OVER (PARTITION BY student_id ORDER BY ts) AS next_location
# # FROM v_all_events_clean
# # WHERE student_id IS NOT NULL
# # ORDER BY student_id, ts
# # """
# # df = pd.read_sql(query, conn)
# # conn.close()

# # # Drop rows where next_location is NULL (last event of student)
# # df = df.dropna(subset=["next_location"]).reset_index(drop=True)
# # print(f"[INFO] Loaded {len(df)} rows from v_all_events_clean")

# # # -----------------------------
# # # 2️⃣ Label encode locations
# # # -----------------------------
# # le = LabelEncoder()
# # df["last_location_enc"] = le.fit_transform(df["last_location"])
# # df["next_location_enc"] = le.transform(df["next_location"])

# # # -----------------------------
# # # 3️⃣ Train RandomForest classifier
# # # -----------------------------
# # X = df[["last_location_enc"]]
# # y = df["next_location_enc"]

# # rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
# # rf.fit(X, y)
# # print("[INFO] RandomForest trained on real data")

# # # -----------------------------
# # # 4️⃣ Train Markov transition table
# # # -----------------------------
# # markov = {}
# # for student in df["student_id"].unique():
# #     student_df = df[df["student_id"] == student]
# #     markov[student] = dict(zip(student_df["last_location"], student_df["next_location"]))
# # print("[INFO] Markov transition table created")

# # # -----------------------------
# # # 5️⃣ Save models
# # # -----------------------------
# # os.makedirs("models", exist_ok=True)
# # joblib.dump(rf, "models/rf_model.pkl")
# # joblib.dump(le, "models/label_encoder.pkl")
# # joblib.dump(markov, "models/markov.pkl")
# # print("✅ Models saved in models/ folder")


# import os
# import joblib
# import pandas as pd
# from sklearn.preprocessing import LabelEncoder
# from sklearn.ensemble import RandomForestClassifier
# import psycopg2

# # -----------------------------
# # 1️⃣ Connect to PostgreSQL
# # -----------------------------
# PG = {
#     "dbname": "sentinel",
#     "user": "admin",
#     "password": "admin",
#     "host": "localhost",
#     "port": 5432
# }

# conn = psycopg2.connect(**PG)
# query = "SELECT student_id, loc AS last_location, lead(loc) OVER (PARTITION BY student_id ORDER BY ts) AS next_location FROM v_all_events_clean"
# df = pd.read_sql(query, conn)
# conn.close()

# print(f"[INFO] Loaded {len(df)} rows from v_all_events_clean")

# # Drop rows where next_location is NULL (end of sequence)
# df = df.dropna(subset=["next_location"])

# # -----------------------------
# # 2️⃣ Label encode locations
# # -----------------------------
# all_locations = pd.concat([df["last_location"], df["next_location"]]).unique()
# le = LabelEncoder()
# le.fit(all_locations)

# df["last_location_enc"] = le.transform(df["last_location"])
# df["next_location_enc"] = le.transform(df["next_location"])

# # -----------------------------
# # 3️⃣ Train RandomForest
# # -----------------------------
# X = df[["last_location_enc"]]
# y = df["next_location_enc"]
# rf = RandomForestClassifier(n_estimators=100, random_state=42)
# rf.fit(X, y)

# # -----------------------------
# # 4️⃣ Save models
# # -----------------------------
# os.makedirs("models", exist_ok=True)
# joblib.dump(rf, "models/rf_model.pkl")
# joblib.dump(le, "models/label_encoder.pkl")

# # -----------------------------
# # 5️⃣ Train Markov transition table
# # -----------------------------
# markov = {}
# for student in df["student_id"].unique():
#     seq_df = df[df["student_id"] == student]
#     markov[student] = dict(zip(seq_df["last_location"], seq_df["next_location"]))

# joblib.dump(markov, "models/markov.pkl")

# print("✅ Models saved in models/ folder")

#!/usr/bin/env python3
"""
Train models from real data in v_all_events_clean.
- RandomForest on top locations (memory-safe)
- Full Markov transition table for all students
"""

import os
import joblib
import pandas as pd
from collections import Counter
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import psycopg2
from psycopg2.extras import RealDictCursor

# ----------------------------
# PostgreSQL connection
# ----------------------------
PG = {"dbname":"sentinel","user":"admin","password":"admin","host":"localhost","port":5432}

conn = psycopg2.connect(**PG, cursor_factory=RealDictCursor)
query = "SELECT * FROM v_all_events_clean ORDER BY ts ASC;"
df = pd.read_sql(query, conn)
conn.close()

print(f"[INFO] Loaded {len(df)} rows from v_all_events_clean")

# ----------------------------
# Reduce unique locations for RandomForest
# ----------------------------
top_n = 50  # top N frequent locations for RF
location_counts = Counter(df["loc"])
top_locations = set([loc for loc, _ in location_counts.most_common(top_n)])

# Filter rows for top locations only
rf_df = df[df["loc"].isin(top_locations)].copy()
rf_df["next_loc"] = rf_df.groupby("student_id")["loc"].shift(-1)
rf_df.dropna(subset=["next_loc"], inplace=True)

print(f"[INFO] Using {len(rf_df)} rows for RandomForest (top {top_n} locations)")

# ----------------------------
# Encode locations
# ----------------------------
le_loc = LabelEncoder()
le_next = LabelEncoder()

rf_df["last_location_enc"] = le_loc.fit_transform(rf_df["loc"])
rf_df["next_location_enc"] = le_next.fit_transform(rf_df["next_loc"])

X = rf_df[["last_location_enc"]]
y = rf_df["next_location_enc"]

# ----------------------------
# Train RandomForest (small, safe)
# ----------------------------
rf = RandomForestClassifier(n_estimators=10, random_state=42)
rf.fit(X, y)
print("[INFO] RandomForest trained successfully")

# ----------------------------
# Train full Markov table for all students
# ----------------------------
markov = {}
for student in df["student_id"].unique():
    student_df = df[df["student_id"]==student].sort_values("ts")
    seq = student_df["loc"].tolist()
    nexts = seq[1:] + [seq[-1]]  # next location for each step
    markov[student] = dict(zip(seq, nexts))

print("[INFO] Markov transition table built")

# ----------------------------
# Save models
# ----------------------------
os.makedirs("models", exist_ok=True)
joblib.dump(rf, "models/rf_model.pkl")
joblib.dump(le_loc, "models/label_encoder_loc.pkl")
joblib.dump(le_next, "models/label_encoder_next.pkl")
joblib.dump(markov, "models/markov.pkl")

print("✅ Models saved in models/ folder")

# backend/app/ml/supervised_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

def create_features(df):
    """Generate tabular features for supervised prediction."""
    df = df.sort_values(["student_id", "ts"])
    df["last_location"] = df.groupby("student_id")["location"].shift(1)
    df["hour"] = df["ts"].dt.hour
    df["dow"] = df["ts"].dt.dayofweek
    df["daypart"] = pd.cut(df["hour"], bins=[0,6,12,18,24], labels=["night","morning","afternoon","evening"], right=False)
    df = df.dropna(subset=["last_location","location"])
    return df

# Load and prepare data
df = pd.read_csv("data/all_events.csv", parse_dates=["ts"])
df_swipes = df[df.event_type.isin(["CARD_SWIPE","WIFI"])].copy()
df_feat = create_features(df_swipes)

# Encode categorical features
enc_loc = LabelEncoder()
df_feat["last_loc_enc"] = enc_loc.fit_transform(df_feat["last_location"])
y = enc_loc.transform(df_feat["location"])

X = df_feat[["last_loc_enc","hour","dow"]]
X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

# Train RandomForest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
joblib.dump(rf, "models/rf_model.pkl")
joblib.dump(enc_loc, "models/label_encoder.pkl")

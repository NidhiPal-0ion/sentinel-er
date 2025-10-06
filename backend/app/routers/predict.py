# # # app/routers/predict.py
# # from fastapi import APIRouter
# # from pydantic import BaseModel
# # from typing import List
# # import pandas as pd
# # import json
# # import datetime

# # router = APIRouter()

# # # Dummy in-memory "historical events" for baseline Markov
# # # Replace with actual DB queries later
# # HISTORICAL_EVENTS = [
# #     {"student_id": "S1", "ts": "2025-09-01 08:00:00", "location": "LIBRARY"},
# #     {"student_id": "S1", "ts": "2025-09-01 10:00:00", "location": "LAB_101"},
# #     {"student_id": "S1", "ts": "2025-09-01 12:00:00", "location": "CAFETERIA"},
# # ]

# # class PredictRequest(BaseModel):
# #     student_id: str
# #     current_time: str  # ISO format

# # class PredictResponse(BaseModel):
# #     predicted_location: str
# #     confidence: float
# #     reasoning: str

# # @router.post("/", response_model=PredictResponse)
# # def predict_next_location(req: PredictRequest):
# #     # Simple baseline: last seen location → predict next most frequent
# #     df = pd.DataFrame(HISTORICAL_EVENTS)
# #     student_events = df[df["student_id"] == req.student_id]
# #     if student_events.empty:
# #         return {
# #             "predicted_location": "UNKNOWN",
# #             "confidence": 0.0,
# #             "reasoning": "No historical data for this student"
# #         }
    
# #     last_location = student_events.iloc[-1]["location"]
    
# #     # Most frequent next location after last_location
# #     # Here just pick most frequent in dataset as dummy
# #     next_loc = student_events["location"].mode()[0]
    
# #     return {
# #         "predicted_location": next_loc,
# #         "confidence": 0.7,  # dummy confidence
# #         "reasoning": f"Based on last known location '{last_location}' and historical frequency"
# #     }
# from fastapi import APIRouter

# router = APIRouter()

# @router.get("/")  # allows GET on /predict/
# def root():
#     return {"message": "Use /predict/{id} to get prediction"}

# @router.get("/{id}")
# def predict(id: str):
#     # placeholder prediction
#     return {"id": id, "prediction": "next_location_example"}
# app/routers/predict.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from collections import defaultdict, Counter
from datetime import datetime
import joblib
import pandas as pd

router = APIRouter()

# PostgreSQL connection settings
PG = {
    "dbname": "sentinel",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": 5432
}

class PredictResponse(BaseModel):
    student_id: str
    predicted_next_location: str
    confidence: float
    reasoning: str

def fetch_student_timeline(student_id: str):
    """Fetch ordered events from v_all_events_clean"""
    conn = psycopg2.connect(**PG, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT loc, ts
        FROM v_all_events_clean
        WHERE student_id=%s
        ORDER BY ts ASC
        """,
        (student_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r["loc"] for r in rows]

def baseline_predict(timeline):
    """Markov / most-frequent location baseline"""
    if not timeline:
        return None, 0.0, "No history available"

    # Simple transition counts (1-step Markov)
    transitions = defaultdict(Counter)
    for i in range(len(timeline)-1):
        transitions[timeline[i]][timeline[i+1]] += 1

    last_loc = timeline[-1]
    if last_loc in transitions and transitions[last_loc]:
        next_loc, count = transitions[last_loc].most_common(1)[0]
        total = sum(transitions[last_loc].values())
        confidence = count / total
        reasoning = f"Most common next location after {last_loc} based on history"
        return next_loc, confidence, reasoning
    else:
        # fallback: most frequent location overall
        freq = Counter(timeline)
        next_loc, count = freq.most_common(1)[0]
        confidence = count / len(timeline)
        reasoning = "Fallback: most frequent location overall"
        return next_loc, confidence, reasoning

@router.get("/{student_id}", response_model=PredictResponse)
def predict(student_id: str):
    timeline = fetch_student_timeline(student_id)
    pred_loc, conf, reasoning = baseline_predict(timeline)
    if pred_loc is None:
        raise HTTPException(status_code=404, detail="No timeline/history for this student")
    return PredictResponse(
        student_id=student_id,
        predicted_next_location=pred_loc,
        confidence=round(conf, 2),
        reasoning=reasoning
    )
    
    
    
    
markov = joblib.load("models/markov.pkl")
rf = joblib.load("models/rf_model.pkl")
enc_loc = joblib.load("models/label_encoder.pkl")

@router.get("/{student_id}")
def predict(student_id: str):
    # Example: last location from DB
    # TODO: fetch last event from Postgres
    last_location = "LAB_101"  # placeholder

    # Markov prediction
    markov_preds = markov.predict_next(last_location)

    # RandomForest prediction
    X_input = pd.DataFrame({"last_loc_enc":[enc_loc.transform([last_location])[0]], "hour":[14], "dow":[2]})
    y_pred = rf.predict(X_input)
    predicted_location = enc_loc.inverse_transform(y_pred)[0]

    return {
        "student_id": student_id,
        "last_location": last_location,
        "markov_prediction": markov_preds,
        "rf_prediction": predicted_location
    }

from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal
import pandas as pd
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/alerts/{entity_id}")
def check_alert(entity_id: str):
    db: Session = SessionLocal()
    logs = pd.read_sql(f"SELECT * FROM all_logs WHERE student_id='{entity_id}'", db.bind)
    if logs.empty:
        return {"alert": "No data available"}
    
    last_seen = logs["timestamp"].max()
    if datetime.now() - last_seen > timedelta(hours=12):
        return {"alert": f"No activity for {entity_id} in last 12 hours"}
    return {"alert": "OK"}

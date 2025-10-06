# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from sqlalchemy import text
# import pandas as pd

# router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.get("/")
# def search_entity(field: str, value: str, db: Session = Depends(get_db)):
#     df = pd.read_sql(text("SELECT * FROM entities_resolved"), db.bind)
    
#     if field not in df.columns:
#         return {"error": f"Field '{field}' not found in entities_resolved"}
    
#     df_matches = df[df[field].astype(str).str.contains(value, case=False, na=False)]
    
#     return {"field": field, "value": value, "matches": df_matches.to_dict(orient="records")}
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from sqlalchemy import text
import pandas as pd

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def search_entity(field: str, value: str, db: Session = Depends(get_db)):
    df = pd.read_sql(text("SELECT * FROM entities_resolved"), db.bind)
    
    if field not in df.columns:
        return {"error": f"Field '{field}' not found in entities_resolved"}
    
    df_matches = df[df[field].astype(str).str.contains(value, case=False, na=False)]
    
    return {"field": field, "value": value, "matches": df_matches.to_dict(orient="records")}

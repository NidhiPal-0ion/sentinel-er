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
# def resolve_entity(query: str, db: Session = Depends(get_db)):
#     # Load resolved entities
#     df = pd.read_sql(text("SELECT * FROM entities_resolved"), db.bind)
    
#     # Case-insensitive substring match on name/email
#     df_matches = df[df['name'].str.contains(query, case=False, na=False) |
#                     df['email'].str.contains(query, case=False, na=False)]
    
#     return {"query": query, "matches": df_matches.to_dict(orient="records")}
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
def resolve_entity(query: str, db: Session = Depends(get_db)):
    df = pd.read_sql(text("SELECT * FROM entities_resolved"), db.bind)
    
    # Match by name or email
    df_matches = df[df['name'].str.contains(query, case=False, na=False) |
                    df['email'].str.contains(query, case=False, na=False)]
    
    return {"query": query, "matches": df_matches.to_dict(orient="records")}

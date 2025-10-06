# from fastapi import APIRouter
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from sqlalchemy import text
# import pandas as pd

# router = APIRouter()

# @router.get("/timeline/{entity_id}")
# def get_timeline(entity_id: str):
#     db: Session = SessionLocal()

#     # Use actual column names (replace 'user_id' if different)
#     query_swipes = text("SELECT * FROM swipes WHERE user_id = :entity_id")
#     query_wifi = text("SELECT * FROM wifi_logs WHERE user_id = :entity_id")
#     query_library = text("SELECT * FROM library WHERE user_id = :entity_id")

#     swipes = pd.read_sql(query_swipes, db.bind, params={"entity_id": entity_id})
#     wifi = pd.read_sql(query_wifi, db.bind, params={"entity_id": entity_id})
#     library = pd.read_sql(query_library, db.bind, params={"entity_id": entity_id})

#     # Combine all logs into a single timeline
#     timeline = pd.concat([swipes, wifi, library], ignore_index=True)
#     timeline = timeline.sort_values("timestamp")

#     return timeline.to_dict(orient="records")
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

# @router.get("/{entity_id}")
# def get_timeline(entity_id: str, db: Session = Depends(get_db)):
#     # Postgres table names (cleaned versions)
#     queries = {
#         "swipes": "SELECT * FROM campus_card_swipes_cleaned WHERE student_id = :entity_id",
#         "wifi": "SELECT * FROM wifi_associations_logs_cleaned WHERE device_hash = :entity_id",
#         "library": "SELECT * FROM library_checkouts_cleaned WHERE student_id = :entity_id",
#         "lab": "SELECT * FROM lab_bookings_cleaned WHERE student_id = :entity_id",
#         "notes": "SELECT * FROM free_text_notes_cleaned WHERE student_id = :entity_id"
# #     }

# #     timeline_dfs = []
# #     for key, query in queries.items():
# #         df = pd.read_sql(text(query), db.bind, params={"entity_id": entity_id})
# #         if not df.empty:
# #             df["event_type"] = key
# #             timeline_dfs.append(df)

# #     if timeline_dfs:
# #         timeline = pd.concat(timeline_dfs, ignore_index=True)
# #         if "timestamp" in timeline.columns:
# #             timeline = timeline.sort_values("timestamp")
# #         return {"entity_id": entity_id, "timeline": timeline.to_dict(orient="records")}
# #     return {"entity_id": entity_id, "timeline": []}
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

# @router.get("/{entity_id}")
# def get_timeline(entity_id: str, db: Session = Depends(get_db)):
#     # Queries for all relevant tables
#     queries = {
#         "swipes": "SELECT * FROM campus_card_swipes_cleaned WHERE student_id = :entity_id",
#         "wifi": "SELECT * FROM wifi_associations_logs_cleaned WHERE device_hash = :entity_id",
#         "library": "SELECT * FROM library_checkouts_cleaned WHERE student_id = :entity_id",
#         "lab": "SELECT * FROM lab_bookings_cleaned WHERE student_id = :entity_id",
#         "notes": "SELECT * FROM free_text_notes_cleaned WHERE student_id = :entity_id"
#     }

#     timeline_dfs = []
#     for key, query in queries.items():
#         df = pd.read_sql(text(query), db.bind, params={"entity_id": entity_id})
#         if not df.empty:
#             df["event_type"] = key
#             timeline_dfs.append(df)

#     if timeline_dfs:
#         timeline = pd.concat(timeline_dfs, ignore_index=True)
#         if "timestamp" in timeline.columns:
#             timeline = timeline.sort_values("timestamp")
#         return {"entity_id": entity_id, "timeline": timeline.to_dict(orient="records")}
#     return {"entity_id": entity_id, "timeline": []}
from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal
from sqlalchemy import text
import pandas as pd

router = APIRouter()

@router.get("/{entity_id}")
def get_timeline(entity_id: str):
    db: Session = SessionLocal()

    # Use cleaned tables and entity_id
    query_swipes = text("SELECT * FROM campus_card_swipes_cleaned WHERE entity_id = :entity_id")
    query_wifi = text("SELECT * FROM wifi_associations_logs_cleaned WHERE entity_id = :entity_id")
    query_library = text("SELECT * FROM library_logs_cleaned WHERE entity_id = :entity_id")

    swipes = pd.read_sql(query_swipes, db.bind, params={"entity_id": entity_id})
    wifi = pd.read_sql(query_wifi, db.bind, params={"entity_id": entity_id})
    library = pd.read_sql(query_library, db.bind, params={"entity_id": entity_id})

    # Combine and sort timeline
    timeline = pd.concat([swipes, wifi, library], ignore_index=True)
    if "timestamp" in timeline.columns:
        timeline = timeline.sort_values("timestamp")
    else:
        timeline["timestamp"] = pd.NaT  # placeholder if missing

    return timeline.to_dict(orient="records")

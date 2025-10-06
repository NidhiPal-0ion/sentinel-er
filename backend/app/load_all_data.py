# # # import os
# # # import pandas as pd
# # # from sqlalchemy import create_engine, text
# # # import ast

# # # # ----------------------------
# # # # 🔹 DATABASE CONNECTION
# # # # ----------------------------
# # # DATABASE_URL = "postgresql://admin:admin@localhost:5432/sentinel"
# # # engine = create_engine(DATABASE_URL)

# # # # ✅ Correct dataset path
# # # BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "Test_Dataset"))
# # # # OR
# # # # BASE_DIR = r"C:\sentinel-er\data\Test_Dataset"

# # # # ----------------------------
# # # # 🔹 TABLE CREATION FUNCTION
# # # # ----------------------------
# # # def create_tables():
# # #     with engine.connect() as conn:
# # #         # Drop existing tables
# # #         tables = [
# # #             "profiles",
# # #             "face_embeddings",
# # #             "campus_card_swipes",
# # #             "wifi_associations_logs",
# # #             "library_checkouts",
# # #             "lab_bookings",
# # #             "free_text_notes",
# # #             "cctv_frames"
# # #         ]
# # #         for table in tables:
# # #             conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))

# # #         # Create profiles table
# # #         conn.execute(text("""
# # #         CREATE TABLE profiles (
# # #             entity_id VARCHAR(50) PRIMARY KEY,
# # #             role VARCHAR(50),
# # #             name VARCHAR(255),
# # #             email VARCHAR(255),
# # #             department VARCHAR(100),
# # #             student_id VARCHAR(50),
# # #             staff_id VARCHAR(50),
# # #             card_id VARCHAR(50),
# # #             device_hash VARCHAR(100),
# # #             face_id VARCHAR(50)
# # #         );
# # #         """))

# # #         # Create face_embeddings table
# # #         conn.execute(text("""
# # #         CREATE TABLE face_embeddings (
# # #             face_id VARCHAR(50) PRIMARY KEY,
# # #             student_id VARCHAR(50),
# # #             embedding FLOAT8[]
# # #         );
# # #         """))

# # #         # Create other tables (simplest structure, modify as per CSV)
# # #         conn.execute(text("""
# # #         CREATE TABLE campus_card_swipes (
# # #             swipe_id SERIAL PRIMARY KEY,
# # #             student_id VARCHAR(50),
# # #             card_id VARCHAR(50),
# # #             timestamp TIMESTAMP
# # #         );
# # #         """))

# # #         conn.execute(text("""
# # #         CREATE TABLE wifi_associations_logs (
# # #             log_id SERIAL PRIMARY KEY,
# # #             device_hash VARCHAR(100),
# # #             ssid VARCHAR(100),
# # #             timestamp TIMESTAMP
# # #         );
# # #         """))

# # #         conn.execute(text("""
# # #         CREATE TABLE library_checkouts (
# # #             checkout_id SERIAL PRIMARY KEY,
# # #             student_id VARCHAR(50),
# # #             book_id VARCHAR(50),
# # #             checkout_date DATE,
# # #             return_date DATE
# # #         );
# # #         """))

# # #         conn.execute(text("""
# # #         CREATE TABLE lab_bookings (
# # #             booking_id SERIAL PRIMARY KEY,
# # #             student_id VARCHAR(50),
# # #             lab_id VARCHAR(50),
# # #             start_time TIMESTAMP,
# # #             end_time TIMESTAMP
# # #         );
# # #         """))

# # #         conn.execute(text("""
# # #         CREATE TABLE free_text_notes (
# # #             note_id SERIAL PRIMARY KEY,
# # #             entity_id VARCHAR(50),
# # #             note TEXT,
# # #             timestamp TIMESTAMP
# # #         );
# # #         """))

# # #         conn.execute(text("""
# # #         CREATE TABLE cctv_frames (
# # #             frame_id SERIAL PRIMARY KEY,
# # #             camera_id VARCHAR(50),
# # #             timestamp TIMESTAMP,
# # #             file_path TEXT
# # #         );
# # #         """))

# # #         conn.commit()
# # #         print("✅ All tables created successfully.")

# # # # ----------------------------
# # # # 🔹 CSV LOADING FUNCTION
# # # # ----------------------------
# # # def load_csv_to_table(csv_file, table_name, special_case=False):
# # #     csv_path = os.path.join(BASE_DIR, csv_file)

# # #     if not os.path.exists(csv_path):
# # #         raise FileNotFoundError(f"❌ File not found: {csv_path}")

# # #     df = pd.read_csv(csv_path)

# # #     if special_case and "embedding" in df.columns:
# # #         # Convert stringified list to actual list
# # #         df["embedding"] = df["embedding"].apply(lambda x: ast.literal_eval(x))

# # #     df.to_sql(table_name, engine, if_exists="append", index=False)
# # #     print(f"✅ Loaded {len(df)} rows into {table_name}")

# # # # ----------------------------
# # # # 🔹 MAIN EXECUTION
# # # # ----------------------------
# # # if __name__ == "__main__":
# # #     create_tables()

# # #     # Load CSVs
# # #     load_csv_to_table("student or staff profiles.csv", "profiles")
# # #     load_csv_to_table("face_embeddings.csv", "face_embeddings", special_case=True)
# # #     load_csv_to_table("campus card_swipes.csv", "campus_card_swipes")
# # #     load_csv_to_table("wifi_associations_logs.csv", "wifi_associations_logs")
# # #     load_csv_to_table("library_checkouts.csv", "library_checkouts")
# # #     load_csv_to_table("lab_bookings.csv", "lab_bookings")
# # #     load_csv_to_table("free_text_notes (helpdesk or RSVPs).csv", "free_text_notes")
# # #     load_csv_to_table("cctv_frames.csv", "cctv_frames")

# # #     print("🎉 All datasets successfully loaded into Postgres!")


# # import os
# # import pandas as pd
# # from sqlalchemy import create_engine, text
# # import ast

# # # -----------------------------
# # # DATABASE CONFIG
# # # -----------------------------
# # DATABASE_URL = "postgresql://admin:admin@localhost:5432/sentinel"
# # engine = create_engine(DATABASE_URL)

# # # -----------------------------
# # # DATASET PATH
# # # -----------------------------
# # BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "Test_Dataset"))
# # # OR Windows style
# # # BASE_DIR = r"C:\sentinel-er\data\Test_Dataset"

# # # -----------------------------
# # # CREATE TABLES
# # # -----------------------------
# # def create_tables():
# #     with engine.connect() as conn:
# #         # Drop old tables if exist
# #         tables = [
# #             "profiles", "face_embeddings", "campus_card_swipes", "wifi_associations_logs",
# #             "library_checkouts", "lab_bookings", "free_text_notes", "cctv_frames"
# #         ]
# #         for table in tables:
# #             conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))

# #         # Create profiles
# #         conn.execute(text("""
# #         CREATE TABLE profiles (
# #             entity_id VARCHAR(50) PRIMARY KEY,
# #             role VARCHAR(50),
# #             name VARCHAR(255),
# #             email VARCHAR(255),
# #             department VARCHAR(100),
# #             student_id VARCHAR(50),
# #             staff_id VARCHAR(50),
# #             card_id VARCHAR(50),
# #             device_hash VARCHAR(100),
# #             face_id VARCHAR(50)
# #         );
# #         """))

# #         # Create face_embeddings
# #         conn.execute(text("""
# #         CREATE TABLE face_embeddings (
# #             face_id VARCHAR(50) PRIMARY KEY,
# #             student_id VARCHAR(50),
# #             embedding FLOAT8[]
# #         );
# #         """))

# #         # Campus card swipes
# #         conn.execute(text("""
# #         CREATE TABLE campus_card_swipes (
# #             card_id VARCHAR(50),
# #             location_id VARCHAR(50),
# #             timestamp TIMESTAMP
# #         );
# #         """))

# #         # Wifi associations logs
# #         conn.execute(text("""
# #         CREATE TABLE wifi_associations_logs (
# #             device_hash VARCHAR(100),
# #             timestamp TIMESTAMP,
# #             location_id VARCHAR(50)
# #         );
# #         """))

# #         # Library checkouts
# #         conn.execute(text("""
# #         CREATE TABLE library_checkouts (
# #             student_id VARCHAR(50),
# #             book_id VARCHAR(50),
# #             checkout_time TIMESTAMP,
# #             return_time TIMESTAMP
# #         );
# #         """))

# #         # Lab bookings
# #         conn.execute(text("""
# #         CREATE TABLE lab_bookings (
# #             student_id VARCHAR(50),
# #             lab_id VARCHAR(50),
# #             booking_time TIMESTAMP,
# #             duration_minutes INT
# #         );
# #         """))

# #         # Free text notes
# #         conn.execute(text("""
# #         CREATE TABLE free_text_notes (
# #             note_id VARCHAR(50) PRIMARY KEY,
# #             student_id VARCHAR(50),
# #             content TEXT,
# #             created_at TIMESTAMP
# #         );
# #         """))

# #         # CCTV frames
# #         conn.execute(text("""
# #         CREATE TABLE cctv_frames (
# #             frame_id VARCHAR(50) PRIMARY KEY,
# #             camera_id VARCHAR(50),
# #             timestamp TIMESTAMP,
# #             file_path TEXT
# #         );
# #         """))

# #         conn.commit()
# #         print("✅ All tables created successfully.")

# # # -----------------------------
# # # LOAD CSV TO TABLE
# # # -----------------------------
# # def load_csv_to_table(csv_file, table_name, special_case=False):
# #     csv_path = os.path.join(BASE_DIR, csv_file)

# #     if not os.path.exists(csv_path):
# #         print(f"❌ File not found: {csv_path}")
# #         return

# #     df = pd.read_csv(csv_path)

# #     # Special case: face_embeddings column 'embedding' as list
# #     if special_case and "embedding" in df.columns:
# #         df["embedding"] = df["embedding"].apply(lambda x: ast.literal_eval(x))

# #     # Trim whitespaces from columns (common source of errors)
# #     df.columns = [col.strip() for col in df.columns]

# #     # Insert into DB
# #     try:
# #         df.to_sql(table_name, engine, if_exists="append", index=False)
# #         print(f"✅ Loaded {len(df)} rows into {table_name}")
# #     except Exception as e:
# #         print(f"❌ Failed to load {table_name}: {e}")

# # # -----------------------------
# # # MAIN
# # # -----------------------------
# # if __name__ == "__main__":
# #     create_tables()

# #     # Load datasets
# #     load_csv_to_table("student or staff profiles.csv", "profiles")
# #     load_csv_to_table("face_embeddings.csv", "face_embeddings", special_case=True)
# #     load_csv_to_table("campus card_swipes.csv", "campus_card_swipes")
# #     load_csv_to_table("wifi_associations_logs.csv", "wifi_associations_logs")
# #     load_csv_to_table("library_checkouts.csv", "library_checkouts")
# #     load_csv_to_table("lab_bookings.csv", "lab_bookings")
# #     load_csv_to_table("free_text_notes (helpdesk or RSVPs).csv", "free_text_notes")
# #     load_csv_to_table("cctv_frames.csv", "cctv_frames")
    
# #     print("🎉 All datasets successfully loaded into Postgres!")



# import os
# import pandas as pd
# from sqlalchemy import create_engine, text
# import ast

# # -----------------------------
# # DATABASE CONFIG
# # -----------------------------
# DATABASE_URL = "postgresql://admin:admin@localhost:5432/sentinel"
# engine = create_engine(DATABASE_URL)

# # -----------------------------
# # DATASET PATH
# # -----------------------------
# BASE_DIR = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), "..", "..", "data", "Test_Dataset")
# )

# # -----------------------------
# # TABLE SCHEMAS
# # -----------------------------
# TABLE_SCHEMAS = {
#     "profiles": """
#         entity_id VARCHAR(50) PRIMARY KEY,
#         role VARCHAR(50),
#         name VARCHAR(255),
#         email VARCHAR(255),
#         department VARCHAR(100),
#         student_id VARCHAR(50),
#         staff_id VARCHAR(50),
#         card_id VARCHAR(50),
#         device_hash VARCHAR(100),
#         face_id VARCHAR(50)
#     """,
#     "face_embeddings": """
#         face_id VARCHAR(50) PRIMARY KEY,
#         student_id VARCHAR(50),
#         embedding FLOAT8[]
#     """,
#     "campus_card_swipes": """
#         card_id VARCHAR(50),
#         location_id VARCHAR(50),
#         timestamp TIMESTAMP
#     """,
#     "wifi_associations_logs": """
#         device_hash VARCHAR(100),
#         timestamp TIMESTAMP,
#         location_id VARCHAR(50)
#     """,
#     "library_checkouts": """
#         student_id VARCHAR(50),
#         book_id VARCHAR(50),
#         checkout_time TIMESTAMP,
#         return_time TIMESTAMP
#     """,
#     "lab_bookings": """
#         student_id VARCHAR(50),
#         lab_id VARCHAR(50),
#         booking_time TIMESTAMP,
#         duration_minutes INT
#     """,
#     "free_text_notes": """
#         note_id VARCHAR(50) PRIMARY KEY,
#         student_id VARCHAR(50),
#         content TEXT,
#         created_at TIMESTAMP
#     """,
#     "cctv_frames": """
#         frame_id VARCHAR(50) PRIMARY KEY,
#         camera_id VARCHAR(50),
#         timestamp TIMESTAMP,
#         file_path TEXT
#     """
# }

# # -----------------------------
# # CREATE TABLES
# # -----------------------------
# def create_tables():
#     with engine.connect() as conn:
#         for table_name, schema in TABLE_SCHEMAS.items():
#             # Drop table if exists
#             conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
#             # Create table
#             conn.execute(text(f"CREATE TABLE {table_name} ({schema});"))
#         conn.commit()
#         print("✅ All tables created successfully.")

# # -----------------------------
# # LOAD CSV INTO TABLE
# # -----------------------------
# def load_csv_to_table(csv_file, table_name, special_case=False):
#     csv_path = os.path.join(BASE_DIR, csv_file)

#     if not os.path.exists(csv_path):
#         print(f"❌ File not found: {csv_path}")
#         return

#     try:
#         df = pd.read_csv(csv_path)

#         # Trim whitespace from column names
#         df.columns = [col.strip() for col in df.columns]

#         # Special case: embedding column as list
#         if special_case and "embedding" in df.columns:
#             df["embedding"] = df["embedding"].apply(lambda x: ast.literal_eval(x))

#         # Insert into DB
#         df.to_sql(table_name, engine, if_exists="append", index=False)
#         print(f"✅ Loaded {len(df)} rows into {table_name}")

#     except Exception as e:
#         print(f"❌ Failed to load {table_name}: {e}")

# # -----------------------------
# # MAIN
# # -----------------------------
# if __name__ == "__main__":
#     create_tables()

#     datasets = [
#         ("student or staff profiles.csv", "profiles", False),
#         ("face_embeddings.csv", "face_embeddings", True),
#         ("campus card_swipes.csv", "campus_card_swipes", False),
#         ("wifi_associations_logs.csv", "wifi_associations_logs", False),
#         ("library_checkouts.csv", "library_checkouts", False),
#         ("lab_bookings.csv", "lab_bookings", False),
#         ("free_text_notes (helpdesk or RSVPs).csv", "free_text_notes", False),
#         ("cctv_frames.csv", "cctv_frames", False)
#     ]

#     for csv_file, table_name, special_case in datasets:
#         load_csv_to_table(csv_file, table_name, special_case)

#     print("🎉 All datasets successfully loaded into Postgres!")


# load_all_data.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
import ast

# -----------------------------
# DATABASE CONFIG
# -----------------------------
DATABASE_URL = "postgresql://admin:admin@localhost:5432/sentinel"
engine = create_engine(DATABASE_URL)

# -----------------------------
# DATASET PATH
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "Test_Dataset"))

# -----------------------------
# TABLE SCHEMAS
# -----------------------------
TABLE_SCHEMAS = {
    "profiles": """
        entity_id VARCHAR(50) PRIMARY KEY,
        role VARCHAR(50),
        name VARCHAR(255),
        email VARCHAR(255),
        department VARCHAR(100),
        student_id VARCHAR(50),
        staff_id VARCHAR(50),
        card_id VARCHAR(50),
        device_hash VARCHAR(100),
        face_id VARCHAR(50)
    """,
    "face_embeddings": """
        face_id VARCHAR(50) PRIMARY KEY,
        student_id VARCHAR(50),
        embedding FLOAT8[]
    """,
    "campus_card_swipes": """
        card_id VARCHAR(50),
        location_id VARCHAR(50),
        timestamp TIMESTAMP
    """,
    "wifi_associations_logs": """
        device_hash VARCHAR(100),
        timestamp TIMESTAMP,
        location_id VARCHAR(50)
    """,
    "library_checkouts": """
        student_id VARCHAR(50),
        book_id VARCHAR(50),
        checkout_time TIMESTAMP,
        return_time TIMESTAMP
    """,
    "lab_bookings": """
        student_id VARCHAR(50),
        lab_id VARCHAR(50),
        booking_time TIMESTAMP,
        duration_minutes INT
    """,
    "free_text_notes": """
        note_id VARCHAR(50) PRIMARY KEY,
        student_id VARCHAR(50),
        content TEXT,
        created_at TIMESTAMP
    """,
    "cctv_frames": """
        frame_id VARCHAR(50) PRIMARY KEY,
        camera_id VARCHAR(50),
        timestamp TIMESTAMP,
        file_path TEXT
    """
}

# -----------------------------
# CREATE TABLES
# -----------------------------
def create_tables():
    with engine.connect() as conn:
        for table_name, schema in TABLE_SCHEMAS.items():
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
            conn.execute(text(f"CREATE TABLE {table_name} ({schema});"))
        conn.commit()
        print("✅ All tables created successfully.")

# -----------------------------
# LOAD CSV INTO TABLE
# -----------------------------
def load_csv_to_table(csv_file, table_name, column_map=None, special_case=False):
    csv_path = os.path.join(BASE_DIR, csv_file)

    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path)
        df.columns = [col.strip() for col in df.columns]

        # Rename columns if mapping provided
        if column_map:
            df = df.rename(columns=column_map)

        # Special case: embedding column as list
        if special_case and "embedding" in df.columns:
            df["embedding"] = df["embedding"].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else None)

        # Reorder columns to match DB
        db_cols = [col.split()[0] for col in TABLE_SCHEMAS[table_name].split(",")]
        df = df[[c for c in db_cols if c in df.columns]]

        # Load into DB
        df.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"✅ Loaded {len(df)} rows into {table_name}")

    except Exception as e:
        print(f"❌ Failed to load {table_name}: {e}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    create_tables()

    datasets = [
        # CSV filename, table_name, column mapping, special_case
        ("student or staff profiles.csv", "profiles", None, False),
        ("face_embeddings.csv", "face_embeddings", None, True),
        ("campus card_swipes.csv", "campus_card_swipes", None, False),
        ("wifi_associations_logs.csv", "wifi_associations_logs", {
            "device_hash": "device_hash",
            "time": "timestamp",
            "location": "location_id"
        }, False),
        ("library_checkouts.csv", "library_checkouts", {
            "student": "student_id",
            "book": "book_id",
            "checkout": "checkout_time",
            "return": "return_time"
        }, False),
        ("lab_bookings.csv", "lab_bookings", {
            "student": "student_id",
            "lab": "lab_id",
            "time": "booking_time",
            "duration": "duration_minutes"
        }, False),
        ("free_text_notes (helpdesk or RSVPs).csv", "free_text_notes", {
            "id": "note_id",
            "student": "student_id",
            "text": "content",
            "created": "created_at"
        }, False),
        ("cctv_frames.csv", "cctv_frames", {
            "id": "frame_id",
            "camera": "camera_id",
            "time": "timestamp",
            "path": "file_path"
        }, False)
    ]

    for csv_file, table_name, column_map, special_case in datasets:
        load_csv_to_table(csv_file, table_name, column_map, special_case)

    print("🎉 All datasets successfully loaded into Postgres!")

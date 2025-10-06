import pandas as pd
from sqlalchemy import create_engine
import re

# -----------------------------
# DATABASE CONFIG
# -----------------------------
DATABASE_URL = "postgresql://admin:admin@localhost:5432/sentinel"
engine = create_engine(DATABASE_URL)

# -----------------------------
# CLEANING FUNCTIONS
# -----------------------------
def normalize_name(name):
    if pd.isna(name):
        return None
    return re.sub(r'\s+', ' ', name.strip().lower())

def normalize_email(email):
    if pd.isna(email):
        return None
    return email.strip().lower()

def normalize_device_hash(device_hash):
    if pd.isna(device_hash):
        return None
    return device_hash.strip().lower()

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
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)

# -----------------------------
# CLEANING PIPELINES
# -----------------------------
def clean_profiles(df):
    df['name'] = df['name'].apply(normalize_name)
    df['email'] = df['email'].apply(normalize_email)
    df['student_id'] = df['student_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['staff_id'] = df['staff_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['card_id'] = df['card_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['device_hash'] = df['device_hash'].apply(normalize_device_hash)
    df['face_id'] = df['face_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    return df

def clean_face_embeddings(df):
    df['student_id'] = df['student_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    return df

def clean_card_swipes(df):
    df['card_id'] = df['card_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['location_id'] = df['location_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['timestamp'] = df['timestamp'].apply(validate_timestamp)
    return df

def clean_wifi_logs(df):
    df['device_hash'] = df['device_hash'].apply(normalize_device_hash)
    df['location_id'] = df['location_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['timestamp'] = df['timestamp'].apply(validate_timestamp)
    return df

def clean_library_checkouts(df):
    df['student_id'] = df['student_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['book_id'] = df['book_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['checkout_time'] = df['checkout_time'].apply(validate_timestamp)
    df['return_time'] = df['return_time'].apply(validate_timestamp)
    return df

def clean_lab_bookings(df):
    df['student_id'] = df['student_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['lab_id'] = df['lab_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['booking_time'] = df['booking_time'].apply(validate_timestamp)
    return df

def clean_free_text_notes(df):
    df['note_id'] = df['note_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['student_id'] = df['student_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['content'] = df['content'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['created_at'] = df['created_at'].apply(validate_timestamp)
    return df

def clean_cctv_frames(df):
    df['frame_id'] = df['frame_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['camera_id'] = df['camera_id'].apply(lambda x: x.strip() if pd.notna(x) else None)
    df['timestamp'] = df['timestamp'].apply(validate_timestamp)
    df['file_path'] = df['file_path'].apply(lambda x: x.strip() if pd.notna(x) else None)
    return df

# -----------------------------
# MAIN CLEANING SCRIPT
# -----------------------------
def main():
    tables = [
        ('profiles', clean_profiles),
        ('face_embeddings', clean_face_embeddings),
        ('campus_card_swipes', clean_card_swipes),
        ('wifi_associations_logs', clean_wifi_logs),
        ('library_checkouts', clean_library_checkouts),
        ('lab_bookings', clean_lab_bookings),
        ('free_text_notes', clean_free_text_notes),
        ('cctv_frames', clean_cctv_frames)
    ]

    for table_name, clean_func in tables:
        print(f"🔹 Cleaning {table_name}...")
        df = load_table(table_name)
        df_cleaned = clean_func(df)
        print(f"✅ {table_name} cleaned: {len(df_cleaned)} rows")

        # Save cleaned data to new table
        cleaned_table_name = f"{table_name}_cleaned"
        df_cleaned.to_sql(cleaned_table_name, engine, if_exists='replace', index=False)
        print(f"💾 Saved cleaned data to {cleaned_table_name}\n")

    print("🎉 Phase 2 Step 1 (Data Cleaning) complete!")

if __name__ == "__main__":
    main()

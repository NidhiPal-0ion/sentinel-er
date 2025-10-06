#!/usr/bin/env python3
"""
Auto-detect canonical 'item' column names in each cleaned view and create v_all_events_clean.
Run from backend folder with venv active:
python build_v_all_events.py
"""

import psycopg2
from psycopg2.extras import RealDictCursor

PG = {"dbname":"sentinel","user":"admin","password":"admin","host":"localhost","port":5432}

# views we expect to combine (in order)
views = [
    "v_card_swipes_clean",
    "v_wifi_clean",
    "v_library_checkouts_clean",
    "v_lab_bookings_clean",
    "v_cctv_frames_clean",
    "v_free_text_notes_clean"
]

def get_columns(cur, view):
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (view,))
    return [r["column_name"] for r in cur.fetchall()]

def find_item_col(cols):
    # common names we might expect; returns the first that exists
    candidates = ["item_id","item","ap_id","ap","location","location_id","frame_id","note_id"]
    for c in candidates:
        if c in cols:
            return c
    # fallback: any column that's not student_id, ts, date, hour, dow, event_type
    for c in cols:
        if c not in ("student_id","ts","date","hour","dow","event_type"):
            return c
    return None

def main():
    conn = psycopg2.connect(**PG, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    snippets = []
    errors = []
    for v in views:
        # check view exists
        cur.execute("SELECT to_regclass(%s) as reg", (v,))
        exists = cur.fetchone()["reg"]
        if not exists:
            errors.append(f"Missing view: {v}")
            continue
        cols = get_columns(cur, v)
        item_col = find_item_col(cols)
        if not item_col:
            errors.append(f"Cannot find item column for {v}. Columns: {cols}")
            continue
        # build select snippet mapping chosen column -> loc
        snippets.append(f"SELECT student_id, ts, {item_col} AS loc, date, hour, dow, event_type FROM {v}")
        print(f"[OK] {v} -> item column: {item_col}")

    if errors:
        print("ERRORS detected:")
        for e in errors:
            print(" -", e)
        print("Fix missing views/columns then re-run this script.")
        cur.close()
        conn.close()
        return

    create_sql = "CREATE OR REPLACE VIEW v_all_events_clean AS\n" + "\nUNION ALL\n".join(snippets) + ";\n"
    print("\n--- Executing CREATE VIEW for v_all_events_clean ---\n")
    # print(create_sql)  # debug: uncomment to print full SQL
    cur.execute(create_sql)
    conn.commit()
    print("v_all_events_clean created/updated successfully.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()

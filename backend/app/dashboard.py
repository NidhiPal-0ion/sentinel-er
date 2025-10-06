# #!/usr/bin/env python3
# # dashboard.py — Sentinel Streamlit Dashboard

# import os
# import joblib
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# import pydeck as pdk
# from pyvis.network import Network
# import networkx as nx
# from datetime import datetime

# # -------------------------
# # Paths
# # -------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # backend/app
# MODELS_DIR = os.path.join(BASE_DIR, "models")

# # FIXED PATH for data (2 levels up to reach sentinel-er root, then data/Test_Dataset)
# DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "Test_Dataset"))

# # Models
# RF_MODEL_PATH = os.path.join(MODELS_DIR, "rf_model.pkl")
# LE_LOC_PATH = os.path.join(MODELS_DIR, "label_encoder_loc.pkl")
# LE_NEXT_PATH = os.path.join(MODELS_DIR, "label_encoder_next.pkl")
# MARKOV_PATH = os.path.join(MODELS_DIR, "markov.pkl")

# # -------------------------
# # Load models
# # -------------------------
# rf_model = joblib.load(RF_MODEL_PATH)
# label_encoder_loc = joblib.load(LE_LOC_PATH)
# label_encoder_next = joblib.load(LE_NEXT_PATH)
# markov_table = joblib.load(MARKOV_PATH)

# # -------------------------
# # Load events & profiles
# # -------------------------
# # Use your actual filenames
# EVENTS_FILES = [
#     "campus card_swipes.csv",
#     "cctv_frames.csv",
#     "lab_bookings.csv",
#     "library_checkouts.csv",
#     "wifi_associations_logs.csv"
# ]

# # Merge all event CSVs into one dataframe
# events_dfs = []
# for f in EVENTS_FILES:
#     path = os.path.join(DATA_DIR, f)
#     if os.path.exists(path):
#         df = pd.read_csv(path)
#         df["source"] = f  # track which file it came from
#         events_dfs.append(df)

# if events_dfs:
#     events_df = pd.concat(events_dfs, ignore_index=True)
# else:
#     events_df = pd.DataFrame()

# # Profiles CSV
# profiles_csv = os.path.join(DATA_DIR, "student or staff profiles.csv")
# profiles_df = pd.read_csv(profiles_csv)

# # -------------------------
# # Streamlit UI
# # -------------------------
# st.set_page_config(page_title="Sentinel Dashboard", layout="wide")
# st.title("🚀 Sentinel Student Dashboard")

# # 6.1 Profile Card
# st.sidebar.header("Select Student")
# if "student_id" in profiles_df.columns:
#     selected_student = st.sidebar.selectbox("Student ID", profiles_df["student_id"].unique())
#     student_profile = profiles_df[profiles_df["student_id"] == selected_student].iloc[0]

#     st.sidebar.write(f"**Name:** {student_profile.get('name','N/A')}")
#     st.sidebar.write(f"**Last Seen:** {student_profile.get('last_seen','N/A')}")
#     st.sidebar.write("**Quick Stats:**")
#     if "student_id" in events_df.columns:
#         st.sidebar.write(f"- Total Events: {len(events_df[events_df['student_id'] == selected_student])}")
#     else:
#         st.sidebar.write("- Total Events: N/A (no student_id column in events)")

# else:
#     st.sidebar.write("No student_id column in profiles.csv")

# # Filter student events
# if not events_df.empty and "student_id" in events_df.columns:
#     student_events = events_df[events_df["student_id"] == selected_student].sort_values("ts") \
#         if "ts" in events_df.columns else pd.DataFrame()
# else:
#     student_events = pd.DataFrame()

# # 6.2 Timeline Plotly
# if not student_events.empty and "ts" in student_events.columns and "loc" in student_events.columns:
#     st.subheader("Timeline of Student Events")
#     fig = px.scatter(student_events, x="ts", y="loc", hover_data=["source"])
#     st.plotly_chart(fig, use_container_width=True)

# # 6.3 Location Map (pydeck)
# if not student_events.empty and {"lat", "lon"}.issubset(student_events.columns):
#     st.subheader("Location Map")
#     map_data = student_events.dropna(subset=["lat","lon"])
#     if not map_data.empty:
#         st.pydeck_chart(pdk.Deck(
#             map_style='mapbox://styles/mapbox/light-v9',
#             initial_view_state=pdk.ViewState(
#                 latitude=map_data["lat"].mean(),
#                 longitude=map_data["lon"].mean(),
#                 zoom=15,
#             ),
#             layers=[
#                 pdk.Layer(
#                     'ScatterplotLayer',
#                     data=map_data,
#                     get_position='[lon, lat]',
#                     get_color='[200, 30, 0, 160]',
#                     get_radius=10,
#                 )
#             ]
#         ))

# # 6.4 Prediction Card
# st.subheader("Next Location Prediction")
# if not student_events.empty and "loc" in student_events.columns:
#     last_loc = student_events.iloc[-1]["loc"]
#     last_enc = label_encoder_loc.transform([last_loc])[0]
#     pred_enc = rf_model.predict([[last_enc]])[0]
#     pred_loc = label_encoder_next.inverse_transform([pred_enc])[0]
#     st.write(f"**Predicted Next Location:** {pred_loc}")
#     st.write(f"**From Markov Table:** {markov_table.get(selected_student, {}).get(last_loc,'N/A')}")

# # 6.5 Alerts
# st.subheader("Alerts")
# if "last_seen" in student_profile:
#     inactive_threshold = pd.Timestamp.now() - pd.Timedelta(hours=12)
#     last_seen_ts = pd.to_datetime(student_profile.get("last_seen", pd.Timestamp.now()))
#     if last_seen_ts < inactive_threshold:
#         st.warning(f"⚠️ Student inactive for more than 12 hours (Last seen: {last_seen_ts})")
#     else:
#         st.success(f"✅ Active (Last seen: {last_seen_ts})")

# # 6.6 Graph View (Pyvis)
# if not events_df.empty and "student_id" in events_df.columns:
#     st.subheader("Student Interaction Graph")
#     G = nx.Graph()
#     sample_students = events_df["student_id"].dropna().unique()[:10]
#     for s in sample_students:
#         G.add_node(s)
#     if len(sample_students) >= 2:
#         G.add_edge(sample_students[0], sample_students[1])
#     net = Network(height="400px", width="100%")
#     net.from_nx(G)
#     net.save_graph("temp_graph.html")
#     st.components.v1.html(open("temp_graph.html", "r").read(), height=400)

# # 6.7 Caching Example
# @st.cache_data
# def heavy_query():
#     return student_events

# _ = heavy_query()







# dashboard.py
# import os
# import glob
# import json
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# from pyvis.network import Network
# import streamlit.components.v1 as components
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from neo4j import GraphDatabase

# # ------------------------
# # CONFIG - update these
# # ------------------------
# # Postgres: keep as is if default docker-compose
# PG_CONFIG = {
#     "host": "localhost",
#     "port": 5432,
#     "dbname": "sentinel",
#     "user": "admin",
#     "password": "admin"
# }

# # Neo4j - put the password you set
# NEO4J_URI = "bolt://localhost:7687"
# NEO4J_USER = "neo4j"
# NEO4J_PASS = "newpassword"   # <-- REPLACE with your Neo4j password

# # Path to dataset root (used to show photos if available)
# # Adjust if your data folder is elsewhere
# DATASET_FACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "Test_Dataset", "face_images"))

# # ------------------------
# # Utility DB helpers
# # ------------------------
# def get_pg_conn():
#     try:
#         conn = psycopg2.connect(**PG_CONFIG)
#         return conn
#     except Exception as e:
#         st.error(f"Postgres connection failed: {e}")
#         return None

# def table_exists(conn, table_name):
#     q = """
#     SELECT EXISTS (
#        SELECT FROM information_schema.tables 
#        WHERE table_schema = 'public' AND table_name = %s
#     );
#     """
#     with conn.cursor() as cur:
#         cur.execute(q, (table_name,))
#         return cur.fetchone()[0]

# def safe_query(conn, sql, params=None, limit=None):
#     """Run a query and return pandas DataFrame; on error return empty."""
#     try:
#         df = pd.read_sql(sql if not params else sql, conn, params=params)
#         if limit:
#             return df.head(limit)
#         return df
#     except Exception:
#         # fallback: try manual cursor (some environments)
#         try:
#             cur = conn.cursor(cursor_factory=RealDictCursor)
#             cur.execute(sql, params or ())
#             rows = cur.fetchall()
#             return pd.DataFrame(rows)
#         except Exception as e:
#             # don't crash - return empty
#             print("Query failed:", e)
#             return pd.DataFrame()

# # ------------------------
# # Fetch profile
# # ------------------------
# def fetch_profile(conn, query):
#     # Try student_id exact, then email exact, then name LIKE
#     q1 = "SELECT * FROM profiles WHERE student_id = %s LIMIT 1;"
#     q2 = "SELECT * FROM profiles WHERE email = %s LIMIT 1;"
#     q3 = "SELECT * FROM profiles WHERE name ILIKE %s LIMIT 1;"
#     try:
#         cur = conn.cursor(cursor_factory=RealDictCursor)
#         cur.execute(q1, (query,))
#         r = cur.fetchone()
#         if r:
#             return dict(r)
#         cur.execute(q2, (query,))
#         r = cur.fetchone()
#         if r:
#             return dict(r)
#         cur.execute(q3, (f"%{query}%",))
#         r = cur.fetchone()
#         if r:
#             return dict(r)
#         return None
#     except Exception as e:
#         print("fetch_profile error:", e)
#         return None

# # ------------------------
# # Build timeline merged from various tables
# # ------------------------
# def build_timeline(conn, student_id, max_rows=1000):
#     events = []
#     # swipe logs
#     try:
#         if table_exists(conn, "campus_card_swipes"):
#             df = safe_query(conn, "SELECT card_id, location_id, timestamp FROM campus_card_swipes WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
#             for _, r in df.iterrows():
#                 events.append({"source":"swipe", "time": r.get("timestamp"), "detail": f"card:{r.get('card_id')} loc:{r.get('location_id')}"})
#     except Exception:
#         pass

#     # wifi logs (some datasets have student_id, some don't)
#     try:
#         if table_exists(conn, "wifi_associations_logs"):
#             # try with student_id column
#             cur = conn.cursor()
#             # check if student_id column exists
#             cur.execute("""
#                 SELECT column_name FROM information_schema.columns
#                 WHERE table_name='wifi_associations_logs' AND column_name='student_id';
#             """)
#             has_student = bool(cur.rowcount)
#             if has_student:
#                 df = safe_query(conn, "SELECT device_hash, ap_id, timestamp FROM wifi_associations_logs WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
#                 for _, r in df.iterrows():
#                     events.append({"source":"wifi", "time": r.get("timestamp"), "detail": f"ap:{r.get('ap_id')} device:{r.get('device_hash')}"})
#             else:
#                 # fallback: maybe logs cannot be linked to student
#                 pass
#     except Exception:
#         pass

#     # library
#     try:
#         if table_exists(conn, "library_checkouts"):
#             df = safe_query(conn, "SELECT book_id, timestamp FROM library_checkouts WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
#             for _, r in df.iterrows():
#                 events.append({"source":"library", "time": r.get("timestamp"), "detail": f"book:{r.get('book_id')}"})
#     except Exception:
#         pass

#     # lab bookings
#     try:
#         if table_exists(conn, "lab_bookings"):
#             df = safe_query(conn, "SELECT lab_id, start_time, end_time FROM lab_bookings WHERE student_id = %s ORDER BY start_time DESC LIMIT %s;", params=(student_id, max_rows))
#             for _, r in df.iterrows():
#                 stime = r.get("start_time"); etime = r.get("end_time")
#                 events.append({"source":"lab", "time": stime or etime, "detail": f"lab:{r.get('lab_id')} start:{stime} end:{etime}"})
#     except Exception:
#         pass

#     # cctv frames
#     try:
#         if table_exists(conn, "cctv_frames"):
#             df = safe_query(conn, "SELECT image_path, timestamp FROM cctv_frames WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
#             for _, r in df.iterrows():
#                 events.append({"source":"cctv", "time": r.get("timestamp"), "detail": f"frame:{r.get('image_path')}"})
#     except Exception:
#         pass

#     # free text notes
#     try:
#         if table_exists(conn, "free_text_notes"):
#             df = safe_query(conn, "SELECT note, timestamp FROM free_text_notes WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
#             for _, r in df.iterrows():
#                 events.append({"source":"note", "time": r.get("timestamp"), "detail": r.get("note")})
#     except Exception:
#         pass

#     # unify to DataFrame
#     df_events = pd.DataFrame([e for e in events if e.get("time") is not None])
#     if df_events.empty:
#         return df_events
#     # ensure time is datetime
#     df_events["time"] = pd.to_datetime(df_events["time"])
#     df_events = df_events.sort_values("time")
#     return df_events

# # ------------------------
# # Graph builder (pyvis)
# # ------------------------
# def build_graph_html(neo_driver, student_id, out_path="graph.html", limit=200):
#     # try to fetch connected nodes
#     query = """
#     MATCH (p:Person {student_id:$id})-[r]-(n)
#     RETURN p, r, n
#     LIMIT $limit
#     """
#     net = Network(height="550px", width="100%", notebook=False, bgcolor="#ffffff")
#     try:
#         with neo_driver.session() as session:
#             result = session.run(query, {"id": student_id, "limit": limit})
#             # add central node
#             net.add_node(f"P:{student_id}", label=f"Person\n{student_id}", color="red", title=f"Person {student_id}")
#             seen_nodes = set([f"P:{student_id}"])
#             for rec in result:
#                 # rec['p'], rec['r'], rec['n']
#                 node_n = rec["n"]
#                 rel = rec["r"]
#                 # node id fallbacks
#                 try:
#                     nid = node_n.id
#                 except Exception:
#                     # create unique id from properties
#                     nid = f"N:{hash(json.dumps(dict(node_n)))}"
#                 label = ",".join(list(node_n.labels)) if getattr(node_n, "labels", None) else "Node"
#                 props = dict(node_n)
#                 title = "<br>".join([f"{k}: {v}" for k,v in props.items()][:10])
#                 node_key = f"N:{nid}"
#                 if node_key not in seen_nodes:
#                     net.add_node(node_key, label=label, title=title)
#                     seen_nodes.add(node_key)
#                 # edge
#                 rtype = getattr(rel, "type", None) or "REL"
#                 # try get start/end ids - fallback to central node
#                 try:
#                     start_id = f"P:{student_id}"
#                     end_id = node_key
#                     net.add_edge(start_id, end_id, title=str(rtype))
#                 except Exception:
#                     pass
#         net.save_graph(out_path)
#         return out_path
#     except Exception as e:
#         print("Neo4j graph build error:", e)
#         return None

# # ------------------------
# # Try to show image for student if available
# # ------------------------
# def find_face_image(student_id):
#     # try possible patterns inside face_images folder
#     if not os.path.isdir(DATASET_FACE_DIR):
#         return None
#     pats = [
#         os.path.join(DATASET_FACE_DIR, f"{student_id}.*"),
#         os.path.join(DATASET_FACE_DIR, f"*{student_id}*.*")
#     ]
#     for p in pats:
#         files = glob.glob(p)
#         if files:
#             return files[0]
#     return None

# # ------------------------
# # STREAMLIT UI
# # ------------------------
# st.set_page_config(layout="wide", page_title="Sentinel ER Dashboard")
# st.title("🚀 Sentinel ER — Dashboard (Phase 5)")

# # sidebar config
# with st.sidebar:
#     st.header("Config")
#     st.write("DB: use defaults or update PG_CONFIG / NEO4J_PASS in the file.")
#     show_raw = st.checkbox("Show raw timeline table", value=True)
#     st.write("---")
#     st.write("Quick checks:")
#     if st.button("Test DB Connections"):
#         pg = get_pg_conn()
#         if pg:
#             st.success("Postgres OK")
#             pg.close()
#         try:
#             neo = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
#             with neo.session() as s:
#                 r = s.run("RETURN 1 AS ok").single().data()
#             st.success("Neo4j OK")
#             neo.close()
#         except Exception as e:
#             st.error(f"Neo4j connection failed: {e}")

# # main search
# col1, col2 = st.columns([2,3])
# with col1:
#     query = st.text_input("Search student_id / email / name / device_hash", "")
#     if st.button("Search"):
#         pg_conn = get_pg_conn()
#         if not pg_conn:
#             st.stop()
#         profile = fetch_profile(pg_conn, query)
#         if not profile:
#             st.warning("No profile found. Try different query (student_id or name substring).")
#         else:
#             st.subheader("Profile")
#             st.json(profile)
#             # display image if found
#             img = find_face_image(profile.get("student_id") or profile.get("email") or "")
#             if img:
#                 st.image(img, width=180)
#             else:
#                 st.info("No face image found locally for this profile.")

# with col2:
#     st.subheader("Timeline (merged events)")
#     if query:
#         pg = get_pg_conn()
#         if not pg:
#             st.stop()
#         # prefer student_id if profile found
#         prof = fetch_profile(pg, query)
#         sid = prof.get("student_id") if prof else query
#         timeline_df = build_timeline(pg, sid)
#         if timeline_df.empty:
#             st.info("No events found for this entity.")
#         else:
#             # quick plot - scatter by event type
#             if not timeline_df.empty:
#                 timeline_df["event_index"] = timeline_df["source"].astype('category').cat.codes
#                 fig = px.scatter(timeline_df, x="time", y="source", hover_data=["detail"], height=400)
#                 st.plotly_chart(fig, use_container_width=True)
#                 if show_raw:
#                     st.dataframe(timeline_df.sort_values("time", ascending=False).reset_index(drop=True))
#         pg.close()

# st.write("---")
# st.subheader("Graph View (Neo4j)")
# if query:
#     # build graph and show pyvis html
#     neo = None
#     try:
#         neo = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
#         graph_path = os.path.join(os.path.dirname(__file__), "graph.html")
#         out = build_graph_html(neo, (fetch_profile(get_pg_conn(), query).get("student_id") if fetch_profile(get_pg_conn(), query) else query), out_path=graph_path)
#         if out and os.path.exists(out):
#             html = open(out, "r", encoding="utf-8").read()
#             components.html(html, height=550)
#         else:
#             st.info("No Neo4j graph data available for this query.")
#     except Exception as e:
#         st.error(f"Neo4j graph error: {e}")
#     finally:
#         if neo:
#             neo.close()

# st.write("---")
# st.caption("Tip: If timeline is empty, verify CSVs are loaded into Postgres. Graph requires Neo4j migration (Phase 4).")




# import streamlit as st
# import pandas as pd
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from neo4j import GraphDatabase
# from datetime import datetime, timedelta
# import hashlib
# import pydeck as pdk
# import plotly.express as px

# # ---------------------------
# # CONFIG
# # ---------------------------
# PG_CONFIG = {
#     "dbname": "sentinel",
#     "user": "admin",
#     "password": "admin",
#     "host": "localhost",
#     "port": 5432,
# }

# NEO4J_URI = "bolt://localhost:7687"
# NEO4J_USER = "neo4j"
# NEO4J_PASS = "newpassword"   # change to your actual password


# # ---------------------------
# # DB CONNECTION HELPERS
# # ---------------------------
# def get_pg_conn():
#     return psycopg2.connect(**PG_CONFIG, cursor_factory=RealDictCursor)

# def get_neo4j_conn():
#     return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# # ---------------------------
# # DATA HELPERS
# # ---------------------------
# @st.cache_data(ttl=300)
# def get_profile(student_id):
#     conn = get_pg_conn()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM profiles WHERE student_id = %s", (student_id,))
#     row = cur.fetchone()
#     conn.close()
#     return row

# @st.cache_data(ttl=300)
# def search_profiles(query):
#     conn = get_pg_conn()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT student_id, name, email
#         FROM profiles
#         WHERE LOWER(name) LIKE %s OR LOWER(email) LIKE %s OR student_id::TEXT = %s
#         LIMIT 20
#     """, (f"%{query.lower()}%", f"%{query.lower()}%", query))
#     rows = cur.fetchall()
#     conn.close()
#     return rows

# @st.cache_data(ttl=300)
# def get_events(student_id):
#     conn = get_pg_conn()
#     dfs = []
#     for table, ts_col in [
#         ("card_swipes", "timestamp"),
#         ("wifi_associations", "timestamp"),
#         ("library_checkouts", "checkout_time"),
#         ("lab_bookings", "booking_time"),
#         ("cctv_frames", "frame_time"),
#     ]:
#         try:
#             dfs.append(pd.read_sql(
#                 f"SELECT '{table}' as source, {ts_col} as ts, * FROM {table} WHERE student_id = %s",
#                 conn,
#                 params=(student_id,),
#             ))
#         except Exception:
#             pass
#     conn.close()
#     if dfs:
#         return pd.concat(dfs).sort_values("ts")
#     return pd.DataFrame()

# @st.cache_data(ttl=300)
# def get_last_seen(student_id):
#     conn = get_pg_conn()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT MAX(ts) as last_seen FROM (
#             SELECT timestamp as ts FROM card_swipes WHERE student_id=%s
#             UNION
#             SELECT timestamp as ts FROM wifi_associations WHERE student_id=%s
#             UNION
#             SELECT checkout_time as ts FROM library_checkouts WHERE student_id=%s
#             UNION
#             SELECT booking_time as ts FROM lab_bookings WHERE student_id=%s
#         ) t
#     """, (student_id, student_id, student_id, student_id))
#     row = cur.fetchone()
#     conn.close()
#     return row["last_seen"]

# @st.cache_data(ttl=300)
# def get_quick_stats(student_id):
#     conn = get_pg_conn()
#     cur = conn.cursor()
#     cur.execute("SELECT COUNT(*) as c FROM card_swipes WHERE student_id=%s", (student_id,))
#     swipes = cur.fetchone()["c"]
#     cur.execute("SELECT COUNT(*) as c FROM wifi_associations WHERE student_id=%s", (student_id,))
#     wifi = cur.fetchone()["c"]
#     cur.execute("SELECT COUNT(*) as c FROM library_checkouts WHERE student_id=%s", (student_id,))
#     books = cur.fetchone()["c"]
#     conn.close()
#     return {"swipes": swipes, "wifi": wifi, "books": books}

# def get_location_coords(event_row):
#     # Dummy location map
#     mapping = {
#         "card_swipes": (28.545, 77.192),  # Example coords
#         "wifi_associations": (28.546, 77.191),
#         "library_checkouts": (28.547, 77.193),
#         "lab_bookings": (28.548, 77.194),
#     }
#     return mapping.get(event_row["source"], None)

# def build_transition_model(conn):
#     df = pd.read_sql("""
#         SELECT student_id, source, DATE(timestamp) as d
#         FROM card_swipes
#         UNION ALL
#         SELECT student_id, 'wifi_associations', DATE(timestamp) FROM wifi_associations
#     """, conn)
#     transitions = {}
#     for sid, group in df.groupby("student_id"):
#         seq = group.sort_values("d")["source"].tolist()
#         for a, b in zip(seq, seq[1:]):
#             transitions.setdefault(a, {}).setdefault(b, 0)
#             transitions[a][b] += 1
#     return transitions

# def predict_next_location(conn, student_id, transitions):
#     df = pd.read_sql("""
#         SELECT source, timestamp as ts
#         FROM card_swipes WHERE student_id=%s
#         UNION ALL
#         SELECT 'wifi_associations', timestamp FROM wifi_associations WHERE student_id=%s
#         ORDER BY ts DESC LIMIT 1
#     """, conn, params=(student_id, student_id))
#     if df.empty:
#         return None
#     last = df.iloc[0]["source"]
#     if last not in transitions:
#         return None
#     nexts = transitions[last]
#     return max(nexts, key=nexts.get)

# def hours_since_last_activity(conn, student_id):
#     last = get_last_seen(student_id)
#     if last is None:
#         return None
#     return (datetime.now() - last).total_seconds() / 3600

# def global_inactivity_alerts(conn, hours=12):
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT p.student_id, p.name, MAX(t.ts) as last_seen
#         FROM profiles p
#         LEFT JOIN (
#             SELECT student_id, timestamp as ts FROM card_swipes
#             UNION ALL
#             SELECT student_id, timestamp FROM wifi_associations
#         ) t ON p.student_id = t.student_id
#         GROUP BY p.student_id, p.name
#     """)
#     rows = cur.fetchall()
#     alerts = []
#     for r in rows:
#         if r["last_seen"] is None:
#             continue
#         diff = (datetime.now() - r["last_seen"]).total_seconds() / 3600
#         if diff > hours:
#             alerts.append({"student_id": r["student_id"], "name": r["name"], "last_seen": r["last_seen"]})
#     return alerts


# # ---------------------------
# # STREAMLIT APP
# # ---------------------------
# st.set_page_config(page_title="Sentinel ER Dashboard", layout="wide")
# st.title("🚀 Sentinel-ER Dashboard")

# query = st.sidebar.text_input("Search student (name/email/id)")
# if query:
#     results = search_profiles(query)
#     if results:
#         choice = st.sidebar.selectbox("Select Profile", [f"{r['student_id']} - {r['name']}" for r in results])
#         sid = choice.split(" - ")[0]
#         profile = get_profile(sid)

#         if profile:
#             # --- Profile Card ---
#             cols = st.columns([1, 3])
#             with cols[0]:
#                 h = hashlib.md5(str(profile.get("student_id")).encode()).hexdigest()
#                 st.image(f"https://robohash.org/{h}.png?set=set5", width=120)
#             with cols[1]:
#                 st.subheader(profile.get("name"))
#                 st.markdown(f"**ID:** {profile.get('student_id')}")
#                 st.markdown(f"**Email:** {profile.get('email')}")
#                 st.markdown(f"**Role:** {profile.get('role')}")
#                 last_seen = get_last_seen(profile.get("student_id"))
#                 st.markdown(f"**Last Seen:** {last_seen}")
#                 stats = get_quick_stats(profile.get("student_id"))
#                 st.markdown(f"Swipes: {stats['swipes']} | Wifi: {stats['wifi']} | Books: {stats['books']}")

#             # --- Prediction ---
#             pg = get_pg_conn()
#             model = build_transition_model(pg)
#             pred = predict_next_location(pg, profile.get("student_id"), model)
#             if pred:
#                 st.info(f"📍 Likely next location: **{pred}**")

#             # --- Alerts ---
#             hrs = hours_since_last_activity(pg, profile.get("student_id"))
#             if hrs is None:
#                 st.warning("No activity records found for this profile.")
#             elif hrs >= 12:
#                 st.error(f"⚠️ No activity in last {hrs:.1f} hours")
#             else:
#                 st.success(f"✅ Last activity {hrs:.1f} hrs ago")

#             if st.sidebar.button("Show global inactivity alerts"):
#                 rows = global_inactivity_alerts(pg, 12)
#                 if rows:
#                     st.subheader("Global Inactivity Alerts")
#                     st.table(rows)
#                 else:
#                     st.success("No global inactivity alerts")

#             # --- Timeline ---
#             df = get_events(profile.get("student_id"))
#             if not df.empty:
#                 fig = px.scatter(df, x="ts", y="source", color="source", hover_data=df.columns)
#                 st.plotly_chart(fig, use_container_width=True)

#                 coords = []
#                 for _, row in df.iterrows():
#                     c = get_location_coords(row)
#                     if c: coords.append({"lat": c[0], "lon": c[1], "label": row["source"]})
#                 if coords:
#                     r = pdk.Deck(
#                         map_style="mapbox://styles/mapbox/light-v9",
#                         initial_view_state=pdk.ViewState(latitude=28.546, longitude=77.192, zoom=15, pitch=30),
#                         layers=[pdk.Layer("ScatterplotLayer", data=coords,
#                                           get_position="[lon, lat]", get_color="[200,30,0,160]",
#                                           get_radius=20)],
#                     )
#                     st.pydeck_chart(r)

#             # --- Graph from Neo4j ---
#             st.subheader("Graph Connections (Neo4j)")
#             with get_neo4j_conn().session() as session:
#                 q = """
#                 MATCH (p:Person {student_id:$sid})-[r]-(n)
#                 RETURN p, r, n LIMIT 25
#                 """
#                 data = session.run(q, sid=profile.get("student_id"))
#                 nodes, edges = set(), []
#                 for rec in data:
#                     nodes.add(str(rec["p"].get("student_id")))
#                     nodes.add(str(rec["n"].get("student_id", rec["n"].get("device_id", rec["n"].get("id")))))
#                     edges.append((rec["p"].get("student_id"), rec["n"].get("student_id", rec["n"].get("device_id", rec["n"].get("id")))))
#                 st.json({"nodes": list(nodes), "edges": edges})

#     else:
#         st.warning("No results found")
# else:
#     st.info("Search a student to begin.")
# dashboard_safe.py
# Paste this into your project and run. It auto-detects table names/columns and
# won't crash if some tables are missing.







#!/usr/bin/env python3
# dashboard.py — Sentinel ER unified Streamlit dashboard
# Place in: C:\sentinel-er\backend\app\dashboard.py
# Data expected at: C:\sentinel-er\data\Test_Dataset\*.csv
# Models expected at: C:\sentinel-er\backend\app\models\*.pkl

# import os
# import glob
# import joblib
# import pandas as pd
# import numpy as np
# import streamlit as st
# import plotly.express as px
# import pydeck as pdk
# from pyvis.network import Network
# import networkx as nx
# from datetime import datetime, timedelta

# # -------------------------
# # Paths (fixed to your structure)
# # -------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))                       # C:\sentinel-er\backend\app
# DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "Test_Dataset"))
# MODELS_DIR = os.path.join(BASE_DIR, "models")

# # model files you said you have
# RF_MODEL_PATH = os.path.join(MODELS_DIR, "rf_model.pkl")
# LE_LOC_PATH = os.path.join(MODELS_DIR, "label_encoder_loc.pkl")
# LE_NEXT_PATH = os.path.join(MODELS_DIR, "label_encoder_next.pkl")
# MARKOV_PATH = os.path.join(MODELS_DIR, "markov.pkl")

# # face images folder (exists in your data)
# FACE_IMG_DIR = os.path.join(DATA_DIR, "face_images")

# # -------------------------
# # Utilities & safe loaders
# # -------------------------
# def safe_load_pickle(path):
#     try:
#         return joblib.load(path)
#     except Exception:
#         return None

# @st.cache_data(ttl=300)
# def load_models():
#     rf = safe_load_pickle(RF_MODEL_PATH)
#     le_loc = safe_load_pickle(LE_LOC_PATH)
#     le_next = safe_load_pickle(LE_NEXT_PATH)
#     markov = safe_load_pickle(MARKOV_PATH) or {}
#     return {"rf": rf, "le_loc": le_loc, "le_next": le_next, "markov": markov}

# def read_csv_if_exists(path, **kwargs):
#     if os.path.exists(path):
#         try:
#             return pd.read_csv(path, **kwargs)
#         except Exception as e:
#             st.warning(f"Failed to read {os.path.basename(path)}: {e}")
#             return pd.DataFrame()
#     return pd.DataFrame()

# # -------------------------
# # Merge / normalize event CSVs -> events_df
# # -------------------------
# @st.cache_data(ttl=300)
# def load_and_unify_events(data_dir):
#     # candidate files (based on your list)
#     mappings = {
#         "campus card_swipes.csv": {"ts": ["timestamp", "ts", "time"], "student": ["student_id", "student", "card_owner", "student_id"], "loc": ["location", "location_id", "loc"]},
#         "wifi_associations_logs.csv": {"ts": ["timestamp", "ts"], "student": ["student_id","device_owner","student"], "loc": ["ap_id","ap","ap_name"]},
#         "library_checkouts.csv": {"ts": ["checkout_time", "checkout", "timestamp"], "student": ["student_id"], "loc":["book_id","item_id"]},
#         "lab_bookings.csv": {"ts": ["booking_time","start_time"], "student": ["student_id"], "loc":["lab_id","lab_name"]},
#         "cctv_frames.csv": {"ts": ["timestamp","ts","frame_time"], "student": ["student_id"], "loc":["camera_id","frame_id"]},
#         "free_text_notes (helpdesk or RSVPs).csv": {"ts": ["created_at","note_time","timestamp"], "student": ["student_id"], "loc": []},
#         "face_embeddings.csv": {"ts": [], "student": ["student_id"], "loc": []},
#         "wifi_associations_logs.csv": {"ts": ["timestamp"], "student": ["student_id"], "loc": ["ap_id"]}
#     }

#     dfs = []
#     for fname, cols_map in mappings.items():
#         path = os.path.join(data_dir, fname)
#         if not os.path.exists(path):
#             continue
#         df = read_csv_if_exists(path)
#         if df.empty:
#             continue

#         # find ts column
#         ts_col = next((c for c in cols_map["ts"] if c in df.columns), None)
#         if ts_col:
#             df = df.rename(columns={ts_col: "ts"})
#         # find student column
#         stud_col = next((c for c in cols_map["student"] if c in df.columns), None)
#         if stud_col:
#             df = df.rename(columns={stud_col: "student_id"})
#         # find loc column
#         loc_col = next((c for c in cols_map["loc"] if c in df.columns), None)
#         if loc_col:
#             df = df.rename(columns={loc_col: "loc"})

#         # standardize minimal columns
#         if "student_id" not in df.columns:
#             # try to infer student from profiles later; keep file but mark student_id NaN
#             df["student_id"] = pd.NA

#         if "ts" not in df.columns:
#             # no timestamp column — skip timeline usefulness but keep metadata
#             df["ts"] = pd.NaT
#         else:
#             df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

#         if "loc" not in df.columns:
#             # create a reasonable loc column depending on file
#             if "book_id" in df.columns:
#                 df["loc"] = df["book_id"].astype(str)
#             elif "lab_id" in df.columns:
#                 df["loc"] = df["lab_id"].astype(str)
#             elif "camera_id" in df.columns:
#                 df["loc"] = df["camera_id"].astype(str)
#             else:
#                 df["loc"] = fname.replace(".csv", "")

#         df["source_file"] = fname
#         dfs.append(df)

#     if not dfs:
#         return pd.DataFrame(columns=["student_id", "ts", "loc", "source_file"])

#     all_events = pd.concat(dfs, ignore_index=True, sort=False)
#     # ensure ts is datetime and sort
#     if "ts" in all_events.columns:
#         all_events["ts"] = pd.to_datetime(all_events["ts"], errors="coerce")
#     all_events = all_events.sort_values("ts", na_position="last").reset_index(drop=True)

#     # derived columns
#     all_events["date"] = all_events["ts"].dt.date
#     all_events["hour"] = all_events["ts"].dt.hour
#     all_events["dow"] = all_events["ts"].dt.dayofweek

#     return all_events

# # -------------------------
# # Load profiles and face embeddings
# # -------------------------
# @st.cache_data(ttl=300)
# def load_profiles_and_faces(data_dir):
#     profiles_path = os.path.join(data_dir, "student or staff profiles.csv")
#     faces_path = os.path.join(data_dir, "face_embeddings.csv")
#     profiles = read_csv_if_exists(profiles_path)
#     faces = read_csv_if_exists(faces_path)
#     # normalize column names
#     profiles_cols = {c: c.strip() for c in profiles.columns}
#     faces_cols = {c: c.strip() for c in faces.columns}
#     profiles.rename(columns=profiles_cols, inplace=True)
#     faces.rename(columns=faces_cols, inplace=True)
#     return profiles, faces

# # -------------------------
# # Search / resolution helpers
# # -------------------------
# def find_profile_by_query(profiles_df, faces_df, query):
#     q = str(query).strip()
#     if q == "":
#         return None

#     # exact student_id match
#     if "student_id" in profiles_df.columns:
#         m = profiles_df[profiles_df["student_id"].astype(str).str.lower() == q.lower()]
#         if not m.empty:
#             return m.iloc[0].to_dict()

#     # exact email
#     if "email" in profiles_df.columns:
#         m = profiles_df[profiles_df["email"].astype(str).str.lower() == q.lower()]
#         if not m.empty:
#             return m.iloc[0].to_dict()

#     # exact face_id in faces -> map to student_id -> profile
#     if "face_id" in faces_df.columns:
#         f = faces_df[faces_df["face_id"].astype(str).str.lower() == q.lower()]
#         if not f.empty:
#             sid = f.iloc[0].get("student_id")
#             if pd.notna(sid) and "student_id" in profiles_df.columns:
#                 m = profiles_df[profiles_df["student_id"].astype(str) == str(sid)]
#                 if not m.empty:
#                     return m.iloc[0].to_dict()
#             # otherwise return face row as minimal profile
#             return {"student_id": sid, "face_id": f.iloc[0].get("face_id")}

#     # exact device/hash match (device_hash or card_id)
#     for dev_col in ("device_hash", "card_id"):
#         if dev_col in profiles_df.columns:
#             m = profiles_df[profiles_df[dev_col].astype(str).str.lower() == q.lower()]
#             if not m.empty:
#                 return m.iloc[0].to_dict()

#     # name contains
#     if "name" in profiles_df.columns:
#         m = profiles_df[profiles_df["name"].astype(str).str.lower().str.contains(q.lower(), na=False)]
#         if not m.empty:
#             return m.iloc[0].to_dict()

#     # fallback: try to treat query as student_id
#     if "student_id" in profiles_df.columns:
#         m = profiles_df[profiles_df["student_id"].astype(str).str.contains(q, na=False)]
#         if not m.empty:
#             return m.iloc[0].to_dict()

#     return None

# # -------------------------
# # Build timeline for profile (accepts student_id OR face_id fallback)
# # -------------------------
# def build_timeline_for_entity(events_df, profiles_df, faces_df, profile):
#     # profile may be dict with student_id (or face_id)
#     sid = profile.get("student_id") if profile else None
#     faceid = profile.get("face_id") if profile else None

#     # if no student_id but faceid present, try to link via faces_df
#     if (not sid or pd.isna(sid)) and faceid and "student_id" in faces_df.columns:
#         linked = faces_df[faces_df["face_id"].astype(str) == str(faceid)]
#         if not linked.empty:
#             sid = linked.iloc[0].get("student_id")

#     # filter events
#     if sid and "student_id" in events_df.columns:
#         e = events_df[events_df["student_id"].astype(str) == str(sid)].copy()
#     else:
#         # fallback: try events with face_id or device hash if available; else best-effort empty
#         e = events_df[events_df.get("face_id") == faceid] if "face_id" in events_df.columns else pd.DataFrame()
#     # ensure sorted
#     if not e.empty and "ts" in e.columns:
#         e = e.sort_values("ts")
#     return e

# # -------------------------
# # Prediction helpers (RF + Markov + simple "reasoning")
# # -------------------------
# def build_global_markov(events_df, top_k_locations=200):
#     # compute transitions globally (from loc to next loc)
#     if events_df.empty or "loc" not in events_df.columns:
#         return {}
#     df = events_df.dropna(subset=["student_id", "loc", "ts"]).sort_values(["student_id", "ts"])
#     transitions = {}
#     for sid, group in df.groupby("student_id"):
#         seq = list(group["loc"])
#         for a, b in zip(seq, seq[1:]):
#             transitions.setdefault(a, {}).setdefault(b, 0)
#             transitions[a][b] += 1
#     return transitions

# def markov_next(loc, transitions):
#     if not loc or loc not in transitions:
#         return None, 0.0
#     nxts = transitions[loc]
#     total = sum(nxts.values())
#     best = max(nxts.items(), key=lambda x: x[1])
#     return best[0], best[1] / total

# def rf_predict_next(loc, models):
#     rf = models.get("rf")
#     le_loc = models.get("le_loc")
#     le_next = models.get("le_next")
#     if rf is None or le_loc is None or le_next is None or loc is None:
#         return None, None
#     try:
#         enc = le_loc.transform([loc])
#     except Exception:
#         return None, None
#     # if model has predict_proba
#     try:
#         proba = rf.predict_proba([enc])[0]
#         pred_idx = int(rf.predict([enc])[0])
#         pred_label = le_next.inverse_transform([pred_idx])[0]
#         conf = float(np.max(proba))
#         #find prob for predicted label if label mapping differs: we used inverse_transform on pred_idx
#         return pred_label, conf
#     except Exception:
#         try:
#             pred_idx = int(rf.predict([enc])[0])
#             pred_label = le_next.inverse_transform([pred_idx])[0]
#             return pred_label, None
#         except Exception:
#             return None, None

# # -------------------------
# # Face image helper
# # -------------------------
# def find_face_images_for_profile(profiles_df_row, faces_df):
#     res = []
#     sid = profiles_df_row.get("student_id")
#     # faces_df may have column 'face_id' and maybe an image path
#     if "student_id" in faces_df.columns:
#         linked = faces_df[faces_df["student_id"].astype(str) == str(sid)]
#         for _, r in linked.iterrows():
#             fid = r.get("face_id")
#             # try common image name patterns in face_images folder
#             if fid:
#                 for ext in ("jpg","jpeg","png"):
#                     p = os.path.join(FACE_IMG_DIR, f"{fid}.{ext}")
#                     if os.path.exists(p):
#                         res.append(p)
#                 # wildcard
#                 matches = glob.glob(os.path.join(FACE_IMG_DIR, f"*{fid}*"))
#                 for m in matches:
#                     if m not in res:
#                         res.append(m)
#     # fallback: maybe profiles row has photo path
#     if profiles_df_row.get("photo_path"):
#         p = os.path.join(DATA_DIR, profiles_df_row.get("photo_path"))
#         if os.path.exists(p) and p not in res:
#             res.insert(0, p)
#     return res

# # -------------------------
# # Load everything once (cached)
# # -------------------------
# models = load_models()
# events_df = load_and_unify_events(DATA_DIR)
# profiles_df, faces_df = load_profiles_and_faces(DATA_DIR)
# global_markov = build_global_markov(events_df)

# # -------------------------
# # Streamlit UI layout
# # -------------------------
# st.set_page_config(page_title="Sentinel ER Dashboard", layout="wide")
# st.title("🚀 Sentinel ER — Unified Dashboard")

# # Search input (accept id, name, email, faceid, device)
# query = st.sidebar.text_input("Search (student_id / name / email / device_hash / face_id)", value="")

# # Quick model info
# with st.sidebar.expander("Models loaded"):
#     st.write(f"RF model: {'loaded' if models.get('rf') is not None else 'NOT loaded'}")
#     st.write(f"Label encoders: loc={'yes' if models.get('le_loc') is not None else 'no'}, next={'yes' if models.get('le_next') is not None else 'no'}")
#     st.write(f"Markov table: {'loaded' if models.get('markov') else 'computed from events'}")
#     st.write(f"Events rows: {len(events_df)}")

# # find profile
# profile = find_profile_by_query(profiles_df, faces_df, query) if query.strip() else None

# if profile is None and query.strip():
#     st.warning("No profile matched exactly. If you entered a face_id or device hash, try different variants. Showing best-effort matches below.")
#     # attempt fuzzy name match in profiles
#     if "name" in profiles_df.columns:
#         fuzzy = profiles_df[profiles_df["name"].astype(str).str.lower().str.contains(query.lower(), na=False)]
#         if not fuzzy.empty:
#             st.write("Closest matches (choose one):")
#             pick = st.selectbox("Pick profile row", fuzzy.apply(lambda r: f"{r['student_id']} | {r.get('name','') } | {r.get('email','')}", axis=1).tolist())
#             if pick:
#                 sid = pick.split("|")[0].strip()
#                 profile = profiles_df[profiles_df["student_id"].astype(str) == sid].iloc[0].to_dict()
#     # also try faces_df for partial matches
#     if profile is None and "face_id" in faces_df.columns:
#         fmatch = faces_df[faces_df["face_id"].astype(str).str.contains(query, na=False)]
#         if not fmatch.empty:
#             first = fmatch.iloc[0]
#             sid = first.get("student_id")
#             profile = {"student_id": sid, "face_id": first.get("face_id")}

# # If still none, show top profiles (helpful)
# if profile is None:
#     st.info("No profile selected yet. Enter a query in the sidebar (student_id / name / email / device_hash / face_id).")
#     # show a small table of profiles for convenience
#     if not profiles_df.empty:
#         st.subheader("Quick sample of profiles")
#         display_cols = [c for c in ["student_id","name","email","department","card_id","device_hash","face_id"] if c in profiles_df.columns]
#         st.dataframe(profiles_df[display_cols].head(20))
#     st.stop()

# # At this point we have a profile dict (may be partial)
# st.header("Profile")
# cols = st.columns([1,3])
# with cols[0]:
#     # show image(s) if any
#     imgs = find_face_images_for_profile(profile, faces_df)
#     if imgs:
#         try:
#             st.image(imgs[0], width=160)
#         except Exception:
#             st.write("Image available:", imgs[0])
#     else:
#         # fallback robohash avatar
#         pid = profile.get("student_id") or profile.get("face_id") or profile.get("email") or "unknown"
#         st.image(f"https://robohash.org/{pid}.png?set=set5", width=160)

# with cols[1]:
#     st.write(f"**Name:** {profile.get('name', 'N/A')}")
#     st.write(f"**Student ID:** {profile.get('student_id', 'N/A')}")
#     st.write(f"**Email:** {profile.get('email', 'N/A')}")
#     st.write(f"**Department:** {profile.get('department', 'N/A')}")
#     st.write(f"**Card ID:** {profile.get('card_id', 'N/A')}")
#     st.write(f"**Device Hash:** {profile.get('device_hash', 'N/A')}")
#     st.write(f"**Face ID:** {profile.get('face_id', 'N/A')}")

# # Build timeline for this entity
# timeline_df = build_timeline_for_entity(events_df, profiles_df, faces_df, profile)

# # Timeline section
# st.subheader("Timeline")
# if timeline_df.empty:
#     st.info("No timeline events found for this entity.")
# else:
#     # use Plotly timeline-ish scatter for zoomable iteration
#     # ensure ts exists
#     if "ts" in timeline_df.columns:
#         fig = px.scatter(timeline_df, x="ts", y="loc", color=timeline_df.get("source_file", timeline_df.get("event_type")), hover_data=timeline_df.columns.tolist(), height=400)
#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.write("Timeline available but no timestamp column present. Showing raw rows.")
#         st.dataframe(timeline_df.head(200))

# # Map section (only if lat/lon available)
# st.subheader("Location Map")
# if not timeline_df.empty and {"lat", "lon"}.issubset(timeline_df.columns):
#     map_df = timeline_df.dropna(subset=["lat","lon"])
#     if not map_df.empty:
#         st.pydeck_chart(pdk.Deck(
#             map_style='mapbox://styles/mapbox/light-v9',
#             initial_view_state=pdk.ViewState(
#                 latitude=map_df["lat"].mean(),
#                 longitude=map_df["lon"].mean(),
#                 zoom=15
#             ),
#             layers=[pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_radius=50)]
#         ))
#     else:
#         st.info("No geolocation (lat/lon) available for this entity's events.")
# else:
#     st.info("Map needs lat & lon columns in event CSVs to display.")

# # Face images gallery
# st.subheader("Face Images")
# imgs = find_face_images_for_profile(profile, faces_df)
# if imgs:
#     cols = st.columns(min(4, len(imgs)))
#     for i, p in enumerate(imgs):
#         try:
#             cols[i % 4].image(p, width=150)
#         except Exception:
#             cols[i % 4].write(p)
# else:
#     st.write("No face images found for this profile in face_images or face_embeddings links.")

# # Prediction card (RF + Markov)
# st.subheader("Prediction — Next Location (explainable)")
# models_for_pred = {"rf": models.get("rf"), "le_loc": models.get("le_loc"), "le_next": models.get("le_next")}
# # build candidate last location
# last_loc = None
# if not timeline_df.empty and "loc" in timeline_df.columns:
#     # get last non-null loc
#     last_series = timeline_df["loc"].dropna()
#     if not last_series.empty:
#         last_loc = last_series.iloc[-1]

# if last_loc is None:
#     st.info("No last location found — cannot predict next location.")
# else:
#     # Markov
#     mk_pred, mk_conf = markov_next(last_loc, global_markov)
#     # RF
#     rf_pred, rf_conf = rf_predict_next(last_loc, models_for_pred)
#     st.write(f"**Last observed location:** {last_loc}")
#     if rf_pred is not None:
#         st.write(f"- **RF predicted next location:** {rf_pred}  {'(confidence: {:.1%})'.format(rf_conf) if rf_conf is not None else ''}")
#     else:
#         st.write("- **RF prediction:** not available (unseen location or model missing)")

#     if mk_pred is not None:
#         st.write(f"- **Markov suggestion:** {mk_pred} (freq confidence: {mk_conf:.1%})")
#     # reasoning: simple textual explanation using RF prob and Markov
#     reasoning = []
#     if rf_pred:
#         if rf_conf is not None:
#             reasoning.append(f"RF model: learned from historical last→next patterns (prob {rf_conf:.1%}).")
#         else:
#             reasoning.append("RF model predicted this location but probability not available.")
#     if mk_pred:
#         reasoning.append(f"Markov: most frequent transition from `{last_loc}` → `{mk_pred}` in training data (freq confidence {mk_conf:.1%}).")
#     if reasoning:
#         st.markdown("**Reasoning:** " + " ".join(reasoning))
#     else:
#         st.markdown("**Reasoning:** No model-based reasoning available.")

# # Alerts (12+ hours inactivity)
# st.subheader("Alerts")
# # compute last seen from timeline or profile last_seen column
# last_seen = None
# if not timeline_df.empty and "ts" in timeline_df.columns:
#     try:
#         last_seen = pd.to_datetime(timeline_df["ts"].dropna()).max()
#     except Exception:
#         last_seen = None
# # fallback profile column names
# if last_seen is None:
#     for c in ("last_seen", "last_seen_at", "last_seen_time"):
#         if c in profile:
#             try:
#                 last_seen = pd.to_datetime(profile.get(c))
#                 break
#             except Exception:
#                 pass

# if last_seen is None:
#     st.info("No last-seen timestamp available to compute inactivity.")
# else:
#     inactive_hours = (pd.Timestamp.now() - pd.to_datetime(last_seen)) / pd.Timedelta(hours=1)
#     if inactive_hours >= 12:
#         st.error(f"⚠️ Inactive for {inactive_hours:.1f} hours (last seen {last_seen})")
#     else:
#         st.success(f"Active — last seen {inactive_hours:.1f} hours ago ({last_seen})")

# # Graph view (small sample around this student)
# st.subheader("Graph View (simple) — connected students/devices")
# G = nx.Graph()
# # add central node
# center = profile.get("student_id") or profile.get("face_id") or "entity"
# G.add_node(center)
# # attempt: connect to other student_ids that appear in same loc within +/-30 minutes
# if not timeline_df.empty and "ts" in timeline_df.columns and "loc" in timeline_df.columns:
#     window = pd.Timedelta(minutes=30)
#     sampled = timeline_df.dropna(subset=["ts","loc"])
#     # for each event of this entity, find others at same loc +- window
#     for _, row in sampled.iterrows():
#         loc = row["loc"]
#         t = pd.to_datetime(row["ts"])
#         others = events_df[(events_df["loc"] == loc) & (pd.to_datetime(events_df["ts"]).between(t - window, t + window))]
#         # add edges to unique student_ids found
#         for _, o in others.iterrows():
#             sid = o.get("student_id")
#             if pd.notna(sid) and sid != profile.get("student_id"):
#                 G.add_node(sid)
#                 G.add_edge(center, sid)
# # draw small graph with pyvis
# net = Network(height="350px", width="100%")
# net.from_nx(G)
# tmp_graph = os.path.join(BASE_DIR, "temp_graph.html")
# net.save_graph(tmp_graph)
# try:
#     with open(tmp_graph, "r", encoding="utf-8") as fh:
#         html = fh.read()
#     st.components.v1.html(html, height=360)
# except Exception:
#     st.write("Graph preview not available.")

# # done
# st.caption("Dashboard assembled from CSVs in `data/Test_Dataset`. Use the search box to locate an entity by id/name/email/device/faceid.")



#!/usr/bin/env python3
"""
Final unified Streamlit dashboard for Sentinel ER.

Place this file at:
  C:\sentinel-er\backend\app\dashboard.py

Data directory (CSV files):
  C:\sentinel-er\data\Test_Dataset\

Models directory:
  C:\sentinel-er\backend\app\models\
    - rf_model.pkl
    - label_encoder_loc.pkl
    - label_encoder_next.pkl
    - markov.pkl
"""

import os
import glob
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import pydeck as pdk
from pyvis.network import Network
import networkx as nx
from datetime import datetime, timedelta


st.set_page_config(page_title="Sentinel ER — Dashboard", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/app
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "Test_Dataset"))
MODELS_DIR = os.path.join(BASE_DIR, "models")
FACE_IMG_DIR = os.path.join(DATA_DIR, "face_images")
DATA_DIR = r"C:\sentinel-er\data\Test_Dataset"
FACE_IMG_DIR = os.path.join(DATA_DIR, "face_images")

# Model paths (try multiple names if present)
RF_MODEL_PATHS = [
    os.path.join(MODELS_DIR, "rf_model.pkl"),
]
LE_LOC_PATHS = [
    os.path.join(MODELS_DIR, "label_encoder_loc.pkl"),
    os.path.join(MODELS_DIR, "label_encoder.pkl"),
]
LE_NEXT_PATHS = [
    os.path.join(MODELS_DIR, "label_encoder_next.pkl"),
    os.path.join(MODELS_DIR, "label_encoder_next_locations.pkl"),
]
MARKOV_PATHS = [
    os.path.join(MODELS_DIR, "markov.pkl"),
]

def find_first_exists(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None

RF_MODEL_PATH = find_first_exists(RF_MODEL_PATHS)
LE_LOC_PATH = find_first_exists(LE_LOC_PATHS)
LE_NEXT_PATH = find_first_exists(LE_NEXT_PATHS)
MARKOV_PATH = find_first_exists(MARKOV_PATHS)

# -------------------------
# Helpers
# -------------------------
def safe_load(path):
    if not path or not os.path.exists(path):
        return None
    try:
        return joblib.load(path)
    except Exception as e:
        st.warning(f"Failed to load {os.path.basename(path)}: {e}")
        return None


def find_face_images(profile, faces_df):
    out = []
    fid = profile.get("face_id")
    if not fid:
        return out

    # Try jpg/png/jpeg
    for ext in ("jpg", "jpeg", "png"):
        path = os.path.join(FACE_IMG_DIR, f"{fid}.{ext}")
        if os.path.exists(path):
            out.append(path)

    # fallback: search folder for any file starting with face_id
    for p in glob.glob(os.path.join(FACE_IMG_DIR, f"{fid}*")):
        if os.path.exists(p) and p not in out:
            out.append(p)

    # return list of paths
    return out

@st.cache_data(ttl=300)
def load_models():
    return {
        "rf": safe_load(RF_MODEL_PATH),
        "le_loc": safe_load(LE_LOC_PATH),
        "le_next": safe_load(LE_NEXT_PATH),
        "markov": safe_load(MARKOV_PATH) or {}
    }

def read_csv_if_exists(path, **kwargs):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path, **kwargs)
    except Exception as e:
        st.warning(f"Could not read CSV {os.path.basename(path)}: {e}")
        return pd.DataFrame()

# canonicalize column names (strip)
def canonicalize_cols(df):
    df.columns = [str(c).strip() for c in df.columns]
    return df

# -------------------------
# Load CSVs & unify events into events_df
# -------------------------
@st.cache_data(ttl=300)
def load_all_sources(data_dir):
    # files expected per your project
    files = {
        "card_swipes": os.path.join(data_dir, "campus card_swipes.csv"),
        "wifi": os.path.join(data_dir, "wifi_associations_logs.csv"),
        "library": os.path.join(data_dir, "library_checkouts.csv"),
        "lab": os.path.join(data_dir, "lab_bookings.csv"),
        "cctv": os.path.join(data_dir, "cctv_frames.csv"),
        "notes": os.path.join(data_dir, "free_text_notes (helpdesk or RSVPs).csv"),
        "faces": os.path.join(data_dir, "face_embeddings.csv"),
    }

    # profiles
    profiles = read_csv_if_exists(os.path.join(data_dir, "student or staff profiles.csv"))
    profiles = canonicalize_cols(profiles)

    # faces table
    faces = read_csv_if_exists(files["faces"])
    faces = canonicalize_cols(faces)

    dfs = []
    # 1) card_swipes: card_id, location_id, timestamp
    df = read_csv_if_exists(files["card_swipes"])
    if not df.empty:
        df = canonicalize_cols(df)
        # try common names
        if "card_id" not in df.columns and "card" in df.columns:
            df = df.rename(columns={"card": "card_id"})
        # map
        col_map = {}
        for c in ("timestamp", "ts", "time"):
            if c in df.columns:
                col_map[c] = "ts"; break
        if "location_id" in df.columns:
            col_map["location_id"] = "loc"
        df = df.rename(columns=col_map)
        df["source"] = "card_swipe"
        dfs.append(df)

    # 2) wifi
    df = read_csv_if_exists(files["wifi"])
    if not df.empty:
        df = canonicalize_cols(df)
        col_map = {}
        for c in ("timestamp","ts"):
            if c in df.columns:
                col_map[c] = "ts"; break
        for c in ("device_hash","device","device_id"):
            if c in df.columns:
                col_map[c] = "device_hash"; break
        for c in ("ap_id","ap"):
            if c in df.columns:
                col_map[c] = "loc"; break
        df = df.rename(columns=col_map)
        df["source"] = "wifi"
        dfs.append(df)

    # 3) library
    df = read_csv_if_exists(files["library"])
    if not df.empty:
        df = canonicalize_cols(df)
        col_map = {}
        for c in ("checkout_time","checkout","timestamp"):
            if c in df.columns:
                col_map[c] = "ts"; break
        if "book_id" in df.columns:
            col_map["book_id"] = "loc"
        df = df.rename(columns=col_map)
        df["source"] = "library"
        dfs.append(df)

    # 4) lab bookings
    df = read_csv_if_exists(files["lab"])
    if not df.empty:
        df = canonicalize_cols(df)
        col_map = {}
        for c in ("booking_time","start_time","timestamp"):
            if c in df.columns:
                col_map[c] = "ts"; break
        if "lab_id" in df.columns:
            col_map["lab_id"] = "loc"
        df = df.rename(columns=col_map)
        df["source"] = "lab"
        dfs.append(df)

    # 5) cctv frames
    df = read_csv_if_exists(files["cctv"])
    if not df.empty:
        df = canonicalize_cols(df)
        col_map = {}
        for c in ("timestamp","ts"):
            if c in df.columns:
                col_map[c] = "ts"; break
        if "camera_id" in df.columns:
            col_map["camera_id"] = "loc"
        # keep file_path if present
        df = df.rename(columns=col_map)
        df["source"] = "cctv"
        dfs.append(df)

    # 6) notes
    df = read_csv_if_exists(files["notes"])
    if not df.empty:
        df = canonicalize_cols(df)
        col_map = {}
        for c in ("created_at","note_time","timestamp"):
            if c in df.columns:
                col_map[c] = "ts"; break
        if "note_id" in df.columns:
            col_map["note_id"] = "note_id"
        if "content" in df.columns:
            col_map["content"] = "content"
        df = df.rename(columns=col_map)
        df["loc"] = df.get("loc", "note")
        df["source"] = "note"
        dfs.append(df)

    # concat
    if not dfs:
        return {"events": pd.DataFrame(columns=["ts","loc","student_id"]), "profiles": profiles, "faces": faces}

    events = pd.concat(dfs, ignore_index=True, sort=False)
    events = canonicalize_cols(events)

    # ensure ts column exists and is datetime
    if "ts" in events.columns:
        events["ts"] = pd.to_datetime(events["ts"], errors="coerce")
    else:
        events["ts"] = pd.NaT

    # Now try to resolve student_id in events using profiles and faces:
    # Add card_id/device_hash/face_id columns if present in events already; otherwise they remain missing.
    # We'll create helper mapping tables
    profile_key_cols = {}
    for c in ("student_id","card_id","device_hash","face_id","email"):
        if c in profiles.columns:
            profile_key_cols[c] = c

    # maps
    card_to_student = {}
    device_to_student = {}
    face_to_student = {}

    if "card_id" in profiles.columns:
        # profiles card->student
        tmp = profiles[["card_id","student_id"]].dropna()
        for _, r in tmp.iterrows():
            card_to_student[str(r["card_id"])] = r["student_id"]
    if "device_hash" in profiles.columns:
        tmp = profiles[["device_hash","student_id"]].dropna()
        for _, r in tmp.iterrows():
            device_to_student[str(r["device_hash"])] = r["student_id"]
    # faces table might map face_id -> student_id
    if "face_id" in faces.columns and "student_id" in faces.columns:
        tmp = faces[["face_id","student_id"]].dropna()
        for _, r in tmp.iterrows():
            face_to_student[str(r["face_id"])] = r["student_id"]

    # fill student_id by checking columns on each row
    def resolve_student_for_row(row):
        # if event has student_id already use it
        sid = row.get("student_id")
        if pd.notna(sid) and sid != "":
            return sid
        # check card_id
        for key in ("card_id","card"):
            if key in row and pd.notna(row.get(key)):
                candidate = str(row.get(key))
                if candidate in card_to_student:
                    return card_to_student[candidate]
        # check device_hash
        for key in ("device_hash","device"):
            if key in row and pd.notna(row.get(key)):
                candidate = str(row.get(key))
                if candidate in device_to_student:
                    return device_to_student[candidate]
        # check face_id
        for key in ("face_id",):
            if key in row and pd.notna(row.get(key)):
                candidate = str(row.get(key))
                if candidate in face_to_student:
                    return face_to_student[candidate]
        return pd.NA

    # create resolution columns if not present
    # apply row-wise resolution (vectorized fallback would be faster but this is robust)
    events["student_id"] = events.apply(resolve_student_for_row, axis=1)

    # Add some derived fields
    events["date"] = pd.to_datetime(events["ts"], errors="coerce").dt.date
    events["hour"] = pd.to_datetime(events["ts"], errors="coerce").dt.hour
    events["dow"] = pd.to_datetime(events["ts"], errors="coerce").dt.dayofweek
    # coerce loc to string
    if "loc" in events.columns:
        events["loc"] = events["loc"].astype(str)
    else:
        events["loc"] = events["source"].astype(str)

    # keep original columns; return
    return {"events": events, "profiles": profiles, "faces": faces}

# -------------------------
# small helpers for prediction/explainability
# -------------------------
def markov_next(loc, markov_table):
    if not loc or not isinstance(loc, str):
        return None, 0.0
    t = markov_table.get(loc)
    if not t:
        return None, 0.0
    total = sum(t.values())
    best_loc, best_count = max(t.items(), key=lambda x: x[1])
    return best_loc, best_count / (total if total>0 else 1)

def rf_predict_next_loc(last_loc, models):
    rf = models.get("rf")
    le_loc = models.get("le_loc")
    le_next = models.get("le_next")
    if rf is None or le_loc is None or le_next is None:
        return None, None
    try:
        enc = le_loc.transform([last_loc])
    except Exception:
        return None, None
    try:
        if hasattr(rf, "predict_proba"):
            probs = rf.predict_proba([enc])[0]
            pred_idx = int(rf.predict([enc])[0])
            pred_label = le_next.inverse_transform([pred_idx])[0]
            conf = float(np.max(probs))
            return pred_label, conf
        else:
            pred_idx = int(rf.predict([enc])[0])
            pred_label = le_next.inverse_transform([pred_idx])[0]
            return pred_label, None
    except Exception:
        return None, None

def find_face_images(profile_row, faces_df):
    out = []
    # check face_id in profile
    fid = profile_row.get("face_id")
    if pd.notna(fid):
        for ext in ("jpg","jpeg","png"):
            path = os.path.join(FACE_IMG_DIR, f"{fid}.{ext}")
            if os.path.exists(path):
                out.append(path)
        # wildcard
        for p in glob.glob(os.path.join(FACE_IMG_DIR, f"*{fid}*")):
            if p not in out:
                out.append(p)
    # check faces_df for face_id -> maybe image_path column exists
    if "face_id" in faces_df.columns:
        matches = faces_df[faces_df["face_id"].astype(str) == str(fid)]
        for _, r in matches.iterrows():
            # possible image path column e.g. 'file_path' or 'image_path'
            for c in ("file_path","image_path","path"):
                if c in r and pd.notna(r[c]):
                    p = os.path.join(DATA_DIR, str(r[c]))
                    if os.path.exists(p) and p not in out:
                        out.append(p)
    # fallback: any file in FACE_IMG_DIR with student_id in name
    sid = profile_row.get("student_id")
    if pd.notna(sid):
        for p in glob.glob(os.path.join(FACE_IMG_DIR, f"*{sid}*")):
            if p not in out:
                out.append(p)
    return out

# -------------------------
# Load data & models
# -------------------------
models = load_models()
data_bundle = load_all_sources(DATA_DIR)
events_df = data_bundle["events"]
profiles_df = data_bundle["profiles"]
faces_df = data_bundle["faces"]
global_markov = models.get("markov") or {}  # prefer loaded markov; otherwise empty

# quick status
st.sidebar.header("Status")
st.sidebar.write(f"CSV folder: {DATA_DIR}")
st.sidebar.write(f"Events rows: {len(events_df)}")
st.sidebar.write(f"Profiles rows: {len(profiles_df)}")
st.sidebar.write(f"Face rows: {len(faces_df)}")
st.sidebar.write("---")
st.sidebar.write(f"RF model loaded: {'yes' if models.get('rf') is not None else 'no'}")
st.sidebar.write(f"Label encoder loc: {'yes' if models.get('le_loc') is not None else 'no'}")
st.sidebar.write(f"Label encoder next: {'yes' if models.get('le_next') is not None else 'no'}")
st.sidebar.write(f"Markov loaded: {'yes' if models.get('markov') else 'no'}")

# -------------------------
# Search box (accept id,name,email,device_hash,face_id)
# -------------------------
query = st.sidebar.text_input("Search (student_id / name / email / device_hash / face_id)", "")

def resolve_profile(query, profiles_df, faces_df):
    q = str(query).strip()
    if q == "":
        return None
    # exact student_id
    for col in ("student_id","entity_id","student"):
        if col in profiles_df.columns:
            match = profiles_df[profiles_df[col].astype(str).str.lower() == q.lower()]
            if not match.empty:
                return match.iloc[0].to_dict()
    # exact email
    if "email" in profiles_df.columns:
        m = profiles_df[profiles_df["email"].astype(str).str.lower() == q.lower()]
        if not m.empty:
            return m.iloc[0].to_dict()
    # exact face_id in faces table
    if "face_id" in faces_df.columns:
        m = faces_df[faces_df["face_id"].astype(str).str.lower() == q.lower()]
        if not m.empty:
            sid = m.iloc[0].get("student_id")
            if pd.notna(sid):
                mm = profiles_df[profiles_df["student_id"].astype(str) == str(sid)]
                if not mm.empty:
                    return mm.iloc[0].to_dict()
            return {"face_id": m.iloc[0].get("face_id"), "student_id": sid}
    # device/card match in profiles
    for c in ("device_hash","card_id"):
        if c in profiles_df.columns:
            m = profiles_df[profiles_df[c].astype(str).str.lower() == q.lower()]
            if not m.empty:
                return m.iloc[0].to_dict()
    # name contains
    if "name" in profiles_df.columns:
        m = profiles_df[profiles_df["name"].astype(str).str.lower().str.contains(q.lower(), na=False)]
        if not m.empty:
            return m.iloc[0].to_dict()
    return None

profile = resolve_profile(query, profiles_df, faces_df) if query.strip() else None

if profile is None and not query.strip():
    st.info("Enter a search (student_id / name / email / device_hash / face_id) in the left panel.")
    st.stop()

if profile is None and query.strip():
    st.warning("No exact profile match. Showing similar profiles (if any).")
    # try fuzzy name suggestions
    if "name" in profiles_df.columns:
        candidates = profiles_df[profiles_df["name"].astype(str).str.lower().str.contains(query.lower(), na=False)]
        if not candidates.empty:
            sel = st.selectbox("Pick a close match", candidates.apply(lambda r: f"{r['student_id']} | {r['name']} | {r.get('email','')}", axis=1).tolist())
            if sel:
                sid = sel.split("|")[0].strip()
                profile = profiles_df[profiles_df["student_id"].astype(str) == sid].iloc[0].to_dict()
    # also try faces
    if profile is None and "face_id" in faces_df.columns:
        ff = faces_df[faces_df["face_id"].astype(str).str.contains(query, na=False)]
        if not ff.empty:
            row = ff.iloc[0]
            sid = row.get("student_id")
            profile = {"student_id": sid, "face_id": row.get("face_id")}

if profile is None:
    st.error("No profile could be resolved from query.")
    st.stop()

# -------------------------
# Show profile card
# -------------------------
st.title("Sentinel ER — Unified Dashboard")
st.header("Profile")
col1, col2 = st.columns([1,3])
with col1:
    imgs = find_face_images(profile, faces_df)
    if imgs:
        try:
            st.image(imgs[0], width=170)
        except Exception:
            st.write(imgs[0])
    else:
        pid = profile.get("student_id") or profile.get("face_id") or profile.get("email") or "unknown"
        st.image(f"https://robohash.org/{pid}.png?set=set5", width=170)

with col2:
    st.write(f"**Name:** {profile.get('name','N/A')}")
    st.write(f"**Student ID:** {profile.get('student_id','N/A')}")
    st.write(f"**Email:** {profile.get('email','N/A')}")
    st.write(f"**Department:** {profile.get('department','N/A')}")
    st.write(f"**Card ID:** {profile.get('card_id','N/A')}")
    st.write(f"**Device Hash:** {profile.get('device_hash','N/A')}")
    st.write(f"**Face ID:** {profile.get('face_id','N/A')}")

# -------------------------
# Build timeline for this profile
# -------------------------
def timeline_for_profile(events_df, profiles_df, faces_df, profile):
    sid = profile.get("student_id")
    fid = profile.get("face_id")
    card = profile.get("card_id")
    dev = profile.get("device_hash")

    # filter by resolved student_id or card/device/face presence
    cond = pd.Series([False]*len(events_df))
    if sid and "student_id" in events_df.columns:
        cond = cond | (events_df["student_id"].astype(str) == str(sid))
    # match by card_id
    if card and "card_id" in events_df.columns:
        cond = cond | (events_df["card_id"].astype(str) == str(card))
    if dev and "device_hash" in events_df.columns:
        cond = cond | (events_df["device_hash"].astype(str) == str(dev))
    if fid and "face_id" in events_df.columns:
        cond = cond | (events_df["face_id"].astype(str) == str(fid))
    # also include events where source_file indicates possible relation (best-effort)
    res = events_df[cond].copy()
    # if none found and sid exists, try fallback: events with resolved student_id equal sid
    if res.empty and sid and "student_id" in events_df.columns:
        res = events_df[events_df["student_id"].astype(str) == str(sid)].copy()
    # sort
    if not res.empty and "ts" in res.columns:
        res = res.sort_values("ts")
    return res

timeline_df = timeline_for_profile(events_df, profiles_df, faces_df, profile)

# -------------------------
# Timeline (plotly)
# -------------------------
st.subheader("Timeline")
if timeline_df.empty:
    st.info("No timeline events found for this entity.")
else:
    # prepare hover columns
    hover_cols = [c for c in timeline_df.columns if c not in ("ts","loc")]
    fig = px.scatter(timeline_df.dropna(subset=["ts"]), x="ts", y="loc", color="source", hover_data=hover_cols, height=420)
    st.plotly_chart(fig, use_container_width=True)
    st.write("Raw timeline (most recent first):")
    st.dataframe(timeline_df.sort_values("ts", ascending=False).reset_index(drop=True).head(200))

# -------------------------
# Location map
# -------------------------
st.subheader("Location Map")
if not timeline_df.empty and {"lat","lon"}.issubset(timeline_df.columns):
    map_df = timeline_df.dropna(subset=["lat","lon"])
    if not map_df.empty:
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(latitude=map_df["lat"].mean(), longitude=map_df["lon"].mean(), zoom=15),
            layers=[pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_radius=50)]
        ))
    else:
        st.info("Timeline has no lat/lon coordinates to show on map.")
else:
    st.info("Map will display only if event CSVs include 'lat' and 'lon' columns.")

# -------------------------
# Face images gallery
# -------------------------
st.subheader("Face Images")
imgs = find_face_images(profile, faces_df)
if imgs:
    cols = st.columns(min(4, len(imgs)))
    for i, p in enumerate(imgs):
        try:
            cols[i % 4].image(p, width=150)
        except Exception:
            cols[i % 4].write(p)
else:
    st.write("No local face images discovered for this profile.")

# -------------------------
# Prediction card (RF + Markov)
# -------------------------
st.subheader("Prediction: Next Location (RF + Markov)")
last_loc = None
if not timeline_df.empty and "loc" in timeline_df.columns:
    last = timeline_df["loc"].dropna()
    if not last.empty:
        last_loc = last.iloc[-1]

models_loaded = models
if last_loc is None:
    st.info("No last observed location found — cannot predict next location.")
else:
    rf_pred, rf_conf = rf_predict_next_loc(last_loc, models_loaded)
    mk_pred, mk_conf = markov_next(last_loc, global_markov or {})
    if rf_pred:
        st.write(f"RF predicted: **{rf_pred}**" + (f"  (confidence {rf_conf:.1%})" if rf_conf else ""))
    else:
        st.write("RF prediction not available (model missing or unseen last location).")
    if mk_pred:
        st.write(f"Markov suggestion: **{mk_pred}** (freq confidence {mk_conf:.1%})")
    # textual reasoning
    reasons = []
    if rf_pred and rf_conf:
        reasons.append(f"RF model: learned mapping from historical features; confidence {rf_conf:.1%}.")
    if mk_pred:
        reasons.append(f"Markov: most common transition observed from `{last_loc}` → `{mk_pred}`.")
    if reasons:
        st.markdown("**Reasoning:** " + " ".join(reasons))
    else:
        st.markdown("**Reasoning:** No reasoning available (models or data insufficient).")

# -------------------------
# Alerts: inactivity > 12hrs
# -------------------------
st.subheader("Alerts")
last_seen = None
if not timeline_df.empty and "ts" in timeline_df.columns:
    try:
        last_seen = pd.to_datetime(timeline_df["ts"].dropna()).max()
    except Exception:
        last_seen = None
# try profile fields
if last_seen is None:
    for maybe in ("last_seen","last_seen_at","last_seen_time","last_seen_timestamp"):
        if maybe in profile:
            try:
                last_seen = pd.to_datetime(profile.get(maybe))
                break
            except Exception:
                pass
if last_seen is None:
    st.info("No last-seen timestamp available to compute inactivity/alerts.")
else:
    hours = (pd.Timestamp.now() - pd.to_datetime(last_seen)) / pd.Timedelta(hours=1)
    if hours >= 12:
        st.error(f"⚠️ No activity for {hours:.1f} hours (last seen {last_seen})")
    else:
        st.success(f"Active — last seen {hours:.1f} hours ago ({last_seen})")

# -------------------------
# Graph view (pyvis) - small neighborhood
# -------------------------
st.subheader("Graph view — nearby interactions (sample)")
G = nx.Graph()
center = profile.get("student_id") or profile.get("face_id") or "entity"
G.add_node(center, label=str(center))
# add neighbors: students seen at same loc in +/-30min windows
if not timeline_df.empty and "ts" in timeline_df.columns and "loc" in timeline_df.columns:
    window = pd.Timedelta(minutes=30)
    small = timeline_df.dropna(subset=["ts","loc"])
    for _, ev in small.iterrows():
        t = pd.to_datetime(ev["ts"])
        loc = ev["loc"]
        others = events_df[(events_df["loc"] == loc) & (pd.to_datetime(events_df["ts"]).between(t - window, t + window))]
        for _, o in others.iterrows():
            sid = o.get("student_id")
            if pd.notna(sid) and sid != profile.get("student_id"):
                G.add_node(sid)
                G.add_edge(center, sid)
# render with pyvis
net = Network(height="360px", width="100%")
net.from_nx(G)
tmp_html = os.path.join(BASE_DIR, "tmp_graph.html")
net.save_graph(tmp_html)
try:
    with open(tmp_html, "r", encoding="utf-8") as fh:
        st.components.v1.html(fh.read(), height=360)
except Exception:
    st.write("Graph preview not available.")

st.caption("Notes: This dashboard unifies CSV sources and resolves events to profiles using card_id/device_hash/face_id when possible. If timeline is empty, verify mapping columns exist in the CSVs (card_id/device_hash/face_id) or check that events contain the student identifier.")

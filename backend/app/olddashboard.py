# # # dashboard.py
# # import os
# # import glob
# # import json
# # import pandas as pd
# # import streamlit as st
# # import plotly.express as px
# # from pyvis.network import Network
# # import streamlit.components.v1 as components
# # import psycopg2
# # from psycopg2.extras import RealDictCursor
# # from neo4j import GraphDatabase

# # # ------------------------
# # # CONFIG - update these
# # # ------------------------
# # # Postgres: keep as is if default docker-compose
# # PG_CONFIG = {
# #     "host": "localhost",
# #     "port": 5432,
# #     "dbname": "sentinel",
# #     "user": "admin",
# #     "password": "admin"
# # }

# # # Neo4j - put the password you set
# # NEO4J_URI = "bolt://localhost:7687"
# # NEO4J_USER = "neo4j"
# # NEO4J_PASS = "newpassword"   # <-- REPLACE with your Neo4j password

# # # Path to dataset root (used to show photos if available)
# # # Adjust if your data folder is elsewhere
# # DATASET_FACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "Test_Dataset", "face_images"))

# # # ------------------------
# # # Utility DB helpers
# # # ------------------------
# # def get_pg_conn():
# #     try:
# #         conn = psycopg2.connect(**PG_CONFIG)
# #         return conn
# #     except Exception as e:
# #         st.error(f"Postgres connection failed: {e}")
# #         return None

# # def table_exists(conn, table_name):
# #     q = """
# #     SELECT EXISTS (
# #        SELECT FROM information_schema.tables 
# #        WHERE table_schema = 'public' AND table_name = %s
# #     );
# #     """
# #     with conn.cursor() as cur:
# #         cur.execute(q, (table_name,))
# #         return cur.fetchone()[0]

# # def safe_query(conn, sql, params=None, limit=None):
# #     """Run a query and return pandas DataFrame; on error return empty."""
# #     try:
# #         df = pd.read_sql(sql if not params else sql, conn, params=params)
# #         if limit:
# #             return df.head(limit)
# #         return df
# #     except Exception:
# #         # fallback: try manual cursor (some environments)
# #         try:
# #             cur = conn.cursor(cursor_factory=RealDictCursor)
# #             cur.execute(sql, params or ())
# #             rows = cur.fetchall()
# #             return pd.DataFrame(rows)
# #         except Exception as e:
# #             # don't crash - return empty
# #             print("Query failed:", e)
# #             return pd.DataFrame()

# # # ------------------------
# # # Fetch profile
# # # ------------------------
# # def fetch_profile(conn, query):
# #     # Try student_id exact, then email exact, then name LIKE
# #     q1 = "SELECT * FROM profiles WHERE student_id = %s LIMIT 1;"
# #     q2 = "SELECT * FROM profiles WHERE email = %s LIMIT 1;"
# #     q3 = "SELECT * FROM profiles WHERE name ILIKE %s LIMIT 1;"
# #     try:
# #         cur = conn.cursor(cursor_factory=RealDictCursor)
# #         cur.execute(q1, (query,))
# #         r = cur.fetchone()
# #         if r:
# #             return dict(r)
# #         cur.execute(q2, (query,))
# #         r = cur.fetchone()
# #         if r:
# #             return dict(r)
# #         cur.execute(q3, (f"%{query}%",))
# #         r = cur.fetchone()
# #         if r:
# #             return dict(r)
# #         return None
# #     except Exception as e:
# #         print("fetch_profile error:", e)
# #         return None

# # # ------------------------
# # # Build timeline merged from various tables
# # # ------------------------
# # def build_timeline(conn, student_id, max_rows=1000):
# #     events = []
# #     # swipe logs
# #     try:
# #         if table_exists(conn, "campus_card_swipes"):
# #             df = safe_query(conn, "SELECT card_id, location_id, timestamp FROM campus_card_swipes WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
# #             for _, r in df.iterrows():
# #                 events.append({"source":"swipe", "time": r.get("timestamp"), "detail": f"card:{r.get('card_id')} loc:{r.get('location_id')}"})
# #     except Exception:
# #         pass

# #     # wifi logs (some datasets have student_id, some don't)
# #     try:
# #         if table_exists(conn, "wifi_associations_logs"):
# #             # try with student_id column
# #             cur = conn.cursor()
# #             # check if student_id column exists
# #             cur.execute("""
# #                 SELECT column_name FROM information_schema.columns
# #                 WHERE table_name='wifi_associations_logs' AND column_name='student_id';
# #             """)
# #             has_student = bool(cur.rowcount)
# #             if has_student:
# #                 df = safe_query(conn, "SELECT device_hash, ap_id, timestamp FROM wifi_associations_logs WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
# #                 for _, r in df.iterrows():
# #                     events.append({"source":"wifi", "time": r.get("timestamp"), "detail": f"ap:{r.get('ap_id')} device:{r.get('device_hash')}"})
# #             else:
# #                 # fallback: maybe logs cannot be linked to student
# #                 pass
# #     except Exception:
# #         pass

# #     # library
# #     try:
# #         if table_exists(conn, "library_checkouts"):
# #             df = safe_query(conn, "SELECT book_id, timestamp FROM library_checkouts WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
# #             for _, r in df.iterrows():
# #                 events.append({"source":"library", "time": r.get("timestamp"), "detail": f"book:{r.get('book_id')}"})
# #     except Exception:
# #         pass

# #     # lab bookings
# #     try:
# #         if table_exists(conn, "lab_bookings"):
# #             df = safe_query(conn, "SELECT lab_id, start_time, end_time FROM lab_bookings WHERE student_id = %s ORDER BY start_time DESC LIMIT %s;", params=(student_id, max_rows))
# #             for _, r in df.iterrows():
# #                 stime = r.get("start_time"); etime = r.get("end_time")
# #                 events.append({"source":"lab", "time": stime or etime, "detail": f"lab:{r.get('lab_id')} start:{stime} end:{etime}"})
# #     except Exception:
# #         pass

# #     # cctv frames
# #     try:
# #         if table_exists(conn, "cctv_frames"):
# #             df = safe_query(conn, "SELECT image_path, timestamp FROM cctv_frames WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
# #             for _, r in df.iterrows():
# #                 events.append({"source":"cctv", "time": r.get("timestamp"), "detail": f"frame:{r.get('image_path')}"})
# #     except Exception:
# #         pass

# #     # free text notes
# #     try:
# #         if table_exists(conn, "free_text_notes"):
# #             df = safe_query(conn, "SELECT note, timestamp FROM free_text_notes WHERE student_id = %s ORDER BY timestamp DESC LIMIT %s;", params=(student_id, max_rows))
# #             for _, r in df.iterrows():
# #                 events.append({"source":"note", "time": r.get("timestamp"), "detail": r.get("note")})
# #     except Exception:
# #         pass

# #     # unify to DataFrame
# #     df_events = pd.DataFrame([e for e in events if e.get("time") is not None])
# #     if df_events.empty:
# #         return df_events
# #     # ensure time is datetime
# #     df_events["time"] = pd.to_datetime(df_events["time"])
# #     df_events = df_events.sort_values("time")
# #     return df_events

# # # ------------------------
# # # Graph builder (pyvis)
# # # ------------------------
# # def build_graph_html(neo_driver, student_id, out_path="graph.html", limit=200):
# #     # try to fetch connected nodes
# #     query = """
# #     MATCH (p:Person {student_id:$id})-[r]-(n)
# #     RETURN p, r, n
# #     LIMIT $limit
# #     """
# #     net = Network(height="550px", width="100%", notebook=False, bgcolor="#ffffff")
# #     try:
# #         with neo_driver.session() as session:
# #             result = session.run(query, {"id": student_id, "limit": limit})
# #             # add central node
# #             net.add_node(f"P:{student_id}", label=f"Person\n{student_id}", color="red", title=f"Person {student_id}")
# #             seen_nodes = set([f"P:{student_id}"])
# #             for rec in result:
# #                 # rec['p'], rec['r'], rec['n']
# #                 node_n = rec["n"]
# #                 rel = rec["r"]
# #                 # node id fallbacks
# #                 try:
# #                     nid = node_n.id
# #                 except Exception:
# #                     # create unique id from properties
# #                     nid = f"N:{hash(json.dumps(dict(node_n)))}"
# #                 label = ",".join(list(node_n.labels)) if getattr(node_n, "labels", None) else "Node"
# #                 props = dict(node_n)
# #                 title = "<br>".join([f"{k}: {v}" for k,v in props.items()][:10])
# #                 node_key = f"N:{nid}"
# #                 if node_key not in seen_nodes:
# #                     net.add_node(node_key, label=label, title=title)
# #                     seen_nodes.add(node_key)
# #                 # edge
# #                 rtype = getattr(rel, "type", None) or "REL"
# #                 # try get start/end ids - fallback to central node
# #                 try:
# #                     start_id = f"P:{student_id}"
# #                     end_id = node_key
# #                     net.add_edge(start_id, end_id, title=str(rtype))
# #                 except Exception:
# #                     pass
# #         net.save_graph(out_path)
# #         return out_path
# #     except Exception as e:
# #         print("Neo4j graph build error:", e)
# #         return None

# # # ------------------------
# # # Try to show image for student if available
# # # ------------------------
# # def find_face_image(student_id):
# #     # try possible patterns inside face_images folder
# #     if not os.path.isdir(DATASET_FACE_DIR):
# #         return None
# #     pats = [
# #         os.path.join(DATASET_FACE_DIR, f"{student_id}.*"),
# #         os.path.join(DATASET_FACE_DIR, f"*{student_id}*.*")
# #     ]
# #     for p in pats:
# #         files = glob.glob(p)
# #         if files:
# #             return files[0]
# #     return None

# # # ------------------------
# # # STREAMLIT UI
# # # ------------------------
# # st.set_page_config(layout="wide", page_title="Sentinel ER Dashboard")
# # st.title("🚀 Sentinel ER — Dashboard (Phase 5)")

# # # sidebar config
# # with st.sidebar:
# #     st.header("Config")
# #     st.write("DB: use defaults or update PG_CONFIG / NEO4J_PASS in the file.")
# #     show_raw = st.checkbox("Show raw timeline table", value=True)
# #     st.write("---")
# #     st.write("Quick checks:")
# #     if st.button("Test DB Connections"):
# #         pg = get_pg_conn()
# #         if pg:
# #             st.success("Postgres OK")
# #             pg.close()
# #         try:
# #             neo = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
# #             with neo.session() as s:
# #                 r = s.run("RETURN 1 AS ok").single().data()
# #             st.success("Neo4j OK")
# #             neo.close()
# #         except Exception as e:
# #             st.error(f"Neo4j connection failed: {e}")

# # # main search
# # col1, col2 = st.columns([2,3])
# # with col1:
# #     query = st.text_input("Search student_id / email / name / device_hash", "")
# #     if st.button("Search"):
# #         pg_conn = get_pg_conn()
# #         if not pg_conn:
# #             st.stop()
# #         profile = fetch_profile(pg_conn, query)
# #         if not profile:
# #             st.warning("No profile found. Try different query (student_id or name substring).")
# #         else:
# #             st.subheader("Profile")
# #             st.json(profile)
# #             # display image if found
# #             img = find_face_image(profile.get("student_id") or profile.get("email") or "")
# #             if img:
# #                 st.image(img, width=180)
# #             else:
# #                 st.info("No face image found locally for this profile.")

# # with col2:
# #     st.subheader("Timeline (merged events)")
# #     if query:
# #         pg = get_pg_conn()
# #         if not pg:
# #             st.stop()
# #         # prefer student_id if profile found
# #         prof = fetch_profile(pg, query)
# #         sid = prof.get("student_id") if prof else query
# #         timeline_df = build_timeline(pg, sid)
# #         if timeline_df.empty:
# #             st.info("No events found for this entity.")
# #         else:
# #             # quick plot - scatter by event type
# #             if not timeline_df.empty:
# #                 timeline_df["event_index"] = timeline_df["source"].astype('category').cat.codes
# #                 fig = px.scatter(timeline_df, x="time", y="source", hover_data=["detail"], height=400)
# #                 st.plotly_chart(fig, use_container_width=True)
# #                 if show_raw:
# #                     st.dataframe(timeline_df.sort_values("time", ascending=False).reset_index(drop=True))
# #         pg.close()

# # st.write("---")
# # st.subheader("Graph View (Neo4j)")
# # if query:
# #     # build graph and show pyvis html
# #     neo = None
# #     try:
# #         neo = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
# #         graph_path = os.path.join(os.path.dirname(__file__), "graph.html")
# #         out = build_graph_html(neo, (fetch_profile(get_pg_conn(), query).get("student_id") if fetch_profile(get_pg_conn(), query) else query), out_path=graph_path)
# #         if out and os.path.exists(out):
# #             html = open(out, "r", encoding="utf-8").read()
# #             components.html(html, height=550)
# #         else:
# #             st.info("No Neo4j graph data available for this query.")
# #     except Exception as e:
# #         st.error(f"Neo4j graph error: {e}")
# #     finally:
# #         if neo:
# #             neo.close()

# # st.write("---")
# # st.caption("Tip: If timeline is empty, verify CSVs are loaded into Postgres. Graph requires Neo4j migration (Phase 4).")
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
# st.title("Sentinel-ER Dashboard")

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

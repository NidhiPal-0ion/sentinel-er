
# import psycopg2
# from psycopg2 import errors
# from neo4j import GraphDatabase

# # -------------------------
# # Config
# # -------------------------
# PG_CONFIG = {
#     "dbname": "sentinel",
#     "user": "admin",
#     "password": "admin",   # <-- replace if needed
#     "host": "localhost",
#     "port": 5432,
# }

# NEO4J_URI = "bolt://localhost:7687"
# NEO4J_USER = "neo4j"
# NEO4J_PASS = "newpassword"   # <-- replace with your neo4j password

# # -------------------------
# # Connectors
# # -------------------------
# pg_conn = psycopg2.connect(**PG_CONFIG)
# pg_cur = pg_conn.cursor()
# neo_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# # -------------------------
# # Migration Functions
# # -------------------------

# def migrate_profiles():
#     print("=== Migrating Profiles ===")
#     try:
#         pg_cur.execute("SELECT student_id, name, email, department, role FROM profiles;")
#     except errors.UndefinedTable:
#         pg_conn.rollback()
#         print("⚠️  profiles table not found, skipping.")
#         return

#     rows = pg_cur.fetchall()
#     migrated, skipped = 0, 0
#     with neo_driver.session() as session:
#         for r in rows:
#             if not r[0]:
#                 skipped += 1
#                 continue
#             session.run("""
#                 MERGE (p:Person {student_id: $student_id})
#                 SET p.name = $name,
#                     p.email = $email,
#                     p.department = $department,
#                     p.role = $role
#             """, {
#                 "student_id": r[0],
#                 "name": r[1],
#                 "email": r[2],
#                 "department": r[3],
#                 "role": r[4],
#             })
#             migrated += 1
#     print(f"✅ Profiles migrated: {migrated}, skipped: {skipped}")


# # def migrate_embeddings():
# #     print("=== Migrating Embeddings ===")
# #     try:
# #         pg_cur.execute("SELECT student_id, embedding FROM face_embeddings;")
# #     except errors.UndefinedTable:
# #         pg_conn.rollback()
# #         print("⚠️  face_embeddings table not found, skipping.")
# #         return

# #     rows = pg_cur.fetchall()
# #     migrated, skipped = 0, 0
# #     with neo_driver.session() as session:
# #         for r in rows:
# #             if not r[0] or not r[1]:
# #                 skipped += 1
# #                 continue
# #             session.run("""
# #                 MATCH (p:Person {student_id: $student_id})
# #                 SET p.embedding = $embedding
# #             """, {"student_id": r[0], "embedding": r[1]})
# #             migrated += 1
# #     print(f"✅ Embeddings migrated: {migrated}, skipped: {skipped}")

# def migrate_embeddings():
#     print("=== Migrating Embeddings ===")
#     try:
#         pg_cur.execute("SELECT student_id, embedding FROM face_embeddings;")
#     except errors.UndefinedTable:
#         pg_conn.rollback()
#         print("⚠️  face_embeddings table not found, skipping.")
#         return

#     rows = pg_cur.fetchall()
#     migrated, skipped = 0, 0
#     with neo_driver.session() as session:
#         for r in rows:
#             student_id = r[0]
#             embedding = r[1]

#             # Skip only if student_id is None or embedding is None / empty
#             if student_id is None or embedding is None or len(embedding) == 0:
#                 skipped += 1
#                 continue

#             # Optional: convert float[] to list for Neo4j
#             emb_list = list(embedding)

#             session.run("""
#                 MATCH (p:Person {student_id: $student_id})
#                 SET p.embedding = $embedding
#             """, {"student_id": student_id, "embedding": emb_list})

#             migrated += 1
#     print(f"✅ Embeddings migrated: {migrated}, skipped: {skipped}")



# def migrate_library_checkouts():
#     print("=== Migrating Library Checkouts ===")
#     try:
#         pg_cur.execute("SELECT student_id, book_id, checkout_time FROM library_checkouts;")
#     except errors.UndefinedTable:
#         pg_conn.rollback()
#         print("⚠️  library_checkouts table not found, skipping.")
#         return

#     rows = pg_cur.fetchall()
#     with neo_driver.session() as session:
#         for r in rows:
#             session.run("""
#                 MATCH (p:Person {student_id: $student_id})
#                 MERGE (b:Book {book_id: $book_id})
#                 MERGE (p)-[:CHECKED_OUT {time: $checkout_time}]->(b)
#             """, {"student_id": r[0], "book_id": r[1], "checkout_time": r[2]})
#     print(f"✅ Library checkouts migrated: {len(rows)}")


# def migrate_lab_bookings():
#     print("=== Migrating Lab Bookings ===")
#     try:
#         pg_cur.execute("SELECT student_id, lab_id, booking_time FROM lab_bookings;")
#     except errors.UndefinedTable:
#         pg_conn.rollback()
#         print("⚠️  lab_bookings table not found, skipping.")
#         return

#     rows = pg_cur.fetchall()
#     with neo_driver.session() as session:
#         for r in rows:
#             session.run("""
#                 MATCH (p:Person {student_id: $student_id})
#                 MERGE (l:Lab {lab_id: $lab_id})
#                 MERGE (p)-[:BOOKED {time: $booking_time}]->(l)
#             """, {"student_id": r[0], "lab_id": r[1], "booking_time": r[2]})
#     print(f"✅ Lab bookings migrated: {len(rows)}")


# def migrate_wifi_logs():
#     print("=== Migrating WiFi Logs ===")
#     try:
#         pg_cur.execute("SELECT COUNT(*) FROM wifi_logs;")
#         total = pg_cur.fetchone()[0]
#         print(f"📊 Found {total} WiFi log records in Postgres")

#         pg_cur.execute("SELECT id, device_hash, ap_id, timestamp FROM wifi_logs;")
#     except errors.UndefinedTable:
#         pg_conn.rollback()
#         print("⚠️  wifi_logs table not found, skipping.")
#         return

#     rows = pg_cur.fetchall()
#     with neo_driver.session() as session:
#         for r in rows:
#             session.run("""
#                 MERGE (d:Device {hash: $device_hash})
#                 MERGE (a:AccessPoint {id: $ap_id})
#                 MERGE (d)-[c:CONNECTED {log_id: $log_id}]->(a)
#                 SET c.timestamp = $ts
#             """, {
#                 "device_hash": r[1],
#                 "ap_id": r[2],
#                 "log_id": r[0],
#                 "ts": r[3]
#             })
#     print(f"✅ WiFi logs migrated: {len(rows)} / {total}")


# # -------------------------
# # Main Runner
# # -------------------------
# if __name__ == "__main__":
#     print("=== Starting migration ===")
#     migrate_profiles()
#     migrate_embeddings()
#     migrate_library_checkouts()
#     migrate_lab_bookings()
#     migrate_wifi_logs()
#     print("=== Migration completed ===")

#     pg_cur.close()
#     pg_conn.close()
#     neo_driver.close()
# migrate_postgres_to_neo4j_final.py




# migrate_postgres_to_neo4j_final.py
import psycopg2
from psycopg2 import errors
from neo4j import GraphDatabase
import json

# -------------------------
# Config
# -------------------------
PG_CONFIG = {
    "dbname": "sentinel",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": 5432,
}

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "newpassword"  # <-- replace with your Neo4j password

# -------------------------
# Connectors
# -------------------------
pg_conn = psycopg2.connect(**PG_CONFIG)
pg_cur = pg_conn.cursor()
neo_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# -------------------------
# Migration Functions
# -------------------------

def migrate_profiles():
    print("=== Migrating Profiles ===")
    try:
        pg_cur.execute("SELECT student_id, name, email, department, role FROM profiles;")
    except errors.UndefinedTable:
        pg_conn.rollback()
        print("⚠️ profiles table not found, skipping.")
        return

    rows = pg_cur.fetchall()
    migrated, skipped = 0, 0
    with neo_driver.session() as session:
        for r in rows:
            if r[0] is None:
                skipped += 1
                continue
            session.run("""
                MERGE (p:Person {student_id: $student_id})
                SET p.name = $name,
                    p.email = $email,
                    p.department = $department,
                    p.role = $role
            """, {
                "student_id": r[0],
                "name": r[1],
                "email": r[2],
                "department": r[3],
                "role": r[4],
            })
            migrated += 1
    print(f"✅ Profiles migrated: {migrated}, skipped: {skipped}")


# def migrate_embeddings():
#     print("=== Migrating Embeddings ===")
#     try:
#         pg_cur.execute("SELECT student_id, embedding FROM face_embeddings;")
#     except errors.UndefinedTable:
#         pg_conn.rollback()
#         print("⚠️ face_embeddings table not found, skipping.")
#         return

#     rows = pg_cur.fetchall()
#     migrated, skipped = 0, 0
#     with neo_driver.session() as session:
#         for r in rows:
#             student_id = r[0]
#             embedding = r[1]

#             if student_id is None or embedding is None or len(embedding) == 0:
#                 skipped += 1
#                 continue

#             # Convert Postgres array to JSON string
#             emb_json = json.dumps(list(embedding))

#             session.run("""
#                 MATCH (p:Person {student_id: $student_id})
#                 SET p.embedding = $embedding
#             """, {"student_id": student_id, "embedding": emb_json})

#             migrated += 1

#     print(f"✅ Embeddings migrated: {migrated}, skipped: {skipped}")
def migrate_embeddings():
    import json
    print("=== Migrating Embeddings ===")
    try:
        pg_cur.execute("SELECT face_id, embedding FROM face_embeddings;")
    except errors.UndefinedTable:
        pg_conn.rollback()
        print("⚠️ face_embeddings table not found, skipping.")
        return

    rows = pg_cur.fetchall()
    migrated, skipped = 0, 0
    with neo_driver.session() as session:
        for r in rows:
            face_id = r[0]
            embedding = r[1]

            if face_id is None or embedding is None or len(embedding) == 0:
                skipped += 1
                continue

            emb_json = json.dumps(list(embedding))

            session.run("""
                MERGE (f:Face {face_id: $face_id})
                SET f.embedding = $embedding
            """, {"face_id": face_id, "embedding": emb_json})

            migrated += 1

    print(f"✅ Face embeddings migrated: {migrated}, skipped: {skipped}")




def migrate_library_checkouts():
    print("=== Migrating Library Checkouts ===")
    try:
        pg_cur.execute("SELECT student_id, book_id, checkout_time FROM library_checkouts;")
    except errors.UndefinedTable:
        pg_conn.rollback()
        print("⚠️ library_checkouts table not found, skipping.")
        return

    rows = pg_cur.fetchall()
    with neo_driver.session() as session:
        for r in rows:
            session.run("""
                MATCH (p:Person {student_id: $student_id})
                MERGE (b:Book {book_id: $book_id})
                MERGE (p)-[:CHECKED_OUT {time: $checkout_time}]->(b)
            """, {"student_id": r[0], "book_id": r[1], "checkout_time": r[2]})
    print(f"✅ Library checkouts migrated: {len(rows)}")


def migrate_lab_bookings():
    print("=== Migrating Lab Bookings ===")
    try:
        pg_cur.execute("SELECT student_id, lab_id, booking_time FROM lab_bookings;")
    except errors.UndefinedTable:
        pg_conn.rollback()
        print("⚠️ lab_bookings table not found, skipping.")
        return

    rows = pg_cur.fetchall()
    with neo_driver.session() as session:
        for r in rows:
            session.run("""
                MATCH (p:Person {student_id: $student_id})
                MERGE (l:Lab {lab_id: $lab_id})
                MERGE (p)-[:BOOKED {time: $booking_time}]->(l)
            """, {"student_id": r[0], "lab_id": r[1], "booking_time": r[2]})
    print(f"✅ Lab bookings migrated: {len(rows)}")


def migrate_wifi_logs():
    print("=== Migrating WiFi Logs ===")
    try:
        pg_cur.execute("SELECT COUNT(*) FROM wifi_logs;")
        total = pg_cur.fetchone()[0]
        print(f"📊 Found {total} WiFi log records in Postgres")

        pg_cur.execute("SELECT id, device_hash, ap_id, timestamp FROM wifi_logs;")
    except errors.UndefinedTable:
        pg_conn.rollback()
        print("⚠️ wifi_logs table not found, skipping.")
        return

    rows = pg_cur.fetchall()
    with neo_driver.session() as session:
        for r in rows:
            session.run("""
                MERGE (d:Device {hash: $device_hash})
                MERGE (a:AccessPoint {id: $ap_id})
                MERGE (d)-[c:CONNECTED {log_id: $log_id}]->(a)
                SET c.timestamp = $ts
            """, {
                "device_hash": r[1],
                "ap_id": r[2],
                "log_id": r[0],
                "ts": r[3]
            })
    print(f"✅ WiFi logs migrated: {len(rows)} / {total}")


# -------------------------
# Main Runner
# -------------------------
if __name__ == "__main__":
    print("=== Starting migration ===")
    migrate_profiles()
    migrate_embeddings()
    migrate_library_checkouts()
    migrate_lab_bookings()
    migrate_wifi_logs()
    print("=== Migration completed ===")

    pg_cur.close()
    pg_conn.close()
    neo_driver.close()

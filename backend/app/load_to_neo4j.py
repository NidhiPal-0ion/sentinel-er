# # import pandas as pd
# # from sqlalchemy import create_engine
# # from services.neo4j_client import Neo4jClient

# # # Postgres
# # pg_engine = create_engine("postgresql://admin:admin@localhost:5432/sentinel")

# # # Neo4j
# # neo = Neo4jClient()

# # # --------- Load from Postgres ---------
# # profiles = pd.read_sql("SELECT * FROM profiles", pg_engine)
# # swipes = pd.read_sql("SELECT * FROM campus_card_swipes", pg_engine)
# # wifi = pd.read_sql("SELECT * FROM wifi_associations_logs", pg_engine)
# # library = pd.read_sql("SELECT * FROM library_checkouts", pg_engine)

# # # --------- Insert into Neo4j ---------
# # with neo.driver.session() as session:
# #     # Profiles as Student/Staff nodes
# #     for _, row in profiles.iterrows():
# #         session.run("""
# #         MERGE (p:Person {student_id: $student_id})
# #         SET p.name = $name, p.email = $email, p.entity_type=$entity_type, p.department=$department
# #         """, dict(row))

# #     # Card swipes → (Person)-[:SWIPED]->(Location)
# #     for _, row in swipes.iterrows():
# #         session.run("""
# #         MERGE (p:Person {student_id: $student_id})
# #         MERGE (l:Location {id: $location_id})
# #         MERGE (p)-[:SWIPED {timestamp:$timestamp}]->(l)
# #         """, dict(row))

# #     # Wifi logs → (Person)-[:CONNECTED]->(AccessPoint)
# #     for _, row in wifi.iterrows():
# #         session.run("""
# #         MERGE (p:Person {student_id: $student_id})
# #         MERGE (ap:AccessPoint {id: $ap_id})
# #         MERGE (p)-[:CONNECTED {timestamp:$timestamp}]->(ap)
# #         """, dict(row))

# #     # Library checkouts → (Person)-[:CHECKED_OUT]->(Book)
# #     for _, row in library.iterrows():
# #         session.run("""
# #         MERGE (p:Person {student_id: $student_id})
# #         MERGE (b:Book {id: $book_id})
# #         MERGE (p)-[:CHECKED_OUT {timestamp:$timestamp}]->(b)
# #         """, dict(row))

# # print("🎉 Neo4j graph loaded successfully!")
# # neo.close()
# import pandas as pd
# from sqlalchemy import create_engine
# from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
# from neo4j import GraphDatabase

# # ---------------------------------------
# # Database configs
# # ---------------------------------------
# POSTGRES_URL = "postgresql://admin:admin@localhost:5432/sentinel"
# NEO4J_URI = "bolt://localhost:7687"
# NEO4J_USER = "neo4j"
# NEO4J_PASS = "newpassword"   
# # ---------------------------------------
# # Connect clients
# # ---------------------------------------
# pg_engine = create_engine(POSTGRES_URL)
# driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# # ---------------------------------------
# # Load Profiles into Neo4j
# # ---------------------------------------
# def load_profiles():
#     profiles = pd.read_sql("SELECT * FROM profiles", pg_engine)
#     print("Profiles loaded from Postgres:", len(profiles))

#     with driver.session() as session:
#         for _, row in profiles.iterrows():
#             params = {
#                 "student_id": row.get("student_id"),
#                 "name": row.get("name", ""),
#                 "email": row.get("email", ""),
#                 "entity_type": row.get("entity_type", ""),
#                 "department": row.get("department", "")
#             }

#             session.run("""
#             MERGE (p:Person {student_id: $student_id})
#             SET p.name = $name, 
#                 p.email = $email, 
#                 p.entity_type = $entity_type, 
#                 p.department = $department
#             """, params)

#     print("✅ Profiles pushed to Neo4j!")


# # ---------------------------------------
# # Main
# # ---------------------------------------
# if __name__ == "__main__":
#     load_profiles()
#     driver.close()
#     print("🎉 Data loading into Neo4j completed successfully!")



import pandas as pd
from sqlalchemy import create_engine
from neo4j import GraphDatabase

# ---------------------------------------
# Database configs
# ---------------------------------------
POSTGRES_URL = "postgresql://admin:admin@localhost:5432/sentinel"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "newpassword"

# ---------------------------------------
# Connect clients
# ---------------------------------------
pg_engine = create_engine(POSTGRES_URL)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# ---------------------------------------
# Load Profiles into Neo4j
# ---------------------------------------
def load_profiles():
    profiles = pd.read_sql("SELECT * FROM profiles", pg_engine)
    print("Profiles loaded from Postgres:", len(profiles))

    with driver.session() as session:
        for _, row in profiles.iterrows():
            student_id = row.get("student_id")
            if not student_id:  # Skip rows with null student_id
                continue

            params = {
                "student_id": student_id,
                "name": row.get("name") or "",
                "email": row.get("email") or "",
                "entity_type": row.get("entity_type") or "",
                "department": row.get("department") or ""
            }

            session.run("""
            MERGE (p:Person {student_id: $student_id})
            SET p.name = $name, 
                p.email = $email, 
                p.entity_type = $entity_type, 
                p.department = $department
            """, params)

    print("✅ Profiles pushed to Neo4j!")

# ---------------------------------------
# Load Card Swipes into Neo4j
# ---------------------------------------
def load_swipes():
    swipes = pd.read_sql("SELECT * FROM campus_card_swipes", pg_engine)
    print("Card swipes loaded:", len(swipes))

    with driver.session() as session:
        for _, row in swipes.iterrows():
            student_id = row.get("student_id")
            location_id = row.get("location_id")
            timestamp = row.get("timestamp")

            if not student_id or not location_id:
                continue

            params = {
                "student_id": student_id,
                "location_id": location_id,
                "timestamp": timestamp
            }

            session.run("""
            MERGE (p:Person {student_id: $student_id})
            MERGE (l:Location {id: $location_id})
            MERGE (p)-[:SWIPED {timestamp:$timestamp}]->(l)
            """, params)
    print("✅ Card swipes pushed to Neo4j!")


# ---------------------------------------
# Load Wifi Logs into Neo4j
# ---------------------------------------
def load_wifi():
    wifi = pd.read_sql("SELECT * FROM wifi_associations_logs", pg_engine)
    print("Wifi logs loaded:", len(wifi))

    with driver.session() as session:
        for _, row in wifi.iterrows():
            student_id = row.get("student_id")
            ap_id = row.get("ap_id")
            timestamp = row.get("timestamp")

            if not student_id or not ap_id:
                continue

            params = {
                "student_id": student_id,
                "ap_id": ap_id,
                "timestamp": timestamp
            }

            session.run("""
            MERGE (p:Person {student_id: $student_id})
            MERGE (ap:AccessPoint {id: $ap_id})
            MERGE (p)-[:CONNECTED {timestamp:$timestamp}]->(ap)
            """, params)
    print("✅ Wifi logs pushed to Neo4j!")


# ---------------------------------------
# Load Library Checkouts into Neo4j
# ---------------------------------------
def load_library():
    library = pd.read_sql("SELECT * FROM library_checkouts", pg_engine)
    print("Library logs loaded:", len(library))

    with driver.session() as session:
        for _, row in library.iterrows():
            student_id = row.get("student_id")
            book_id = row.get("book_id")
            timestamp = row.get("timestamp")

            if not student_id or not book_id:
                continue

            params = {
                "student_id": student_id,
                "book_id": book_id,
                "timestamp": timestamp
            }

            session.run("""
            MERGE (p:Person {student_id: $student_id})
            MERGE (b:Book {id: $book_id})
            MERGE (p)-[:CHECKED_OUT {timestamp:$timestamp}]->(b)
            """, params)
    print("✅ Library logs pushed to Neo4j!")


# ---------------------------------------
# Main
# ---------------------------------------
if __name__ == "__main__":
    load_profiles()
    load_swipes()
    load_wifi()
    load_library()
    driver.close()
    print("🎉 All data loaded into Neo4j successfully!")

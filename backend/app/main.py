# # from fastapi import FastAPI
# # from fastapi.middleware.cors import CORSMiddleware
# # from app.routers import timeline


# # # FastAPI app instance
# # app = FastAPI(
# #     title="Sentinel ER",
# #     description="Campus Entity Resolution & Security Monitoring API",
# #     version="0.1"
# # )

# # app.include_router(timeline.router)

# # # Optional: CORS for frontend (Streamlit / React)
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],  # production me restrict karo
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # @app.get("/")
# # def root():
# #     return {"message": "Sentinel ER API is running"}
# # # Health check endpoint
# # @app.get("/health")
# # def health_check():
# #     return {"status": "ok"}

# # # Example route to test Postgres connection
# # @app.get("/test/postgres")
# # def test_postgres():
# #     import psycopg2
# #     try:
# #         conn = psycopg2.connect(
# #             dbname="sentinel",
# #             user="admin",
# #             password="admin",
# #             host="localhost",
# #             port=5432
# #         )
# #         cur = conn.cursor()
# #         cur.execute("SELECT 1;")
# #         result = cur.fetchone()
# #         cur.close()
# #         conn.close()
# #         return {"postgres": result[0]}
# #     except Exception as e:
# #         return {"error": str(e)}

# # # Example route to test Neo4j connection
# # @app.get("/test/neo4j")
# # def test_neo4j():
# #     from neo4j import GraphDatabase
# #     uri = "bolt://localhost:7687"
# #     user = "neo4j"
# #     password = "test"
# #     try:
# #         driver = GraphDatabase.driver(uri, auth=(user, password))
# #         with driver.session() as session:
# #             result = session.run("RETURN 1 AS test")
# #             val = result.single()["test"]
# #         driver.close()
# #         return {"neo4j": val}
# #     except Exception as e:
# #         return {"error": str(e)}
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routers import timeline, entity_resolution, search

# # FastAPI app instance
# app = FastAPI(
#     title="Sentinel ER",
#     description="Campus Entity Resolution & Security Monitoring API",
#     version="0.1"
# )

# # Include routers
# app.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
# app.include_router(entity_resolution.router, prefix="/entity-resolution", tags=["Entity Resolution"])
# app.include_router(search.router, prefix="/search", tags=["Search"])

# # Optional: CORS for frontend (Streamlit / React)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # production me restrict karo
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# def root():
#     return {"message": "Sentinel ER API is running"}

# @app.get("/health")
# def health_check():
#     return {"status": "ok"}

# # Example route to test Postgres connection
# @app.get("/test/postgres")
# def test_postgres():
#     import psycopg2
#     try:
#         conn = psycopg2.connect(
#             dbname="sentinel",
#             user="admin",
#             password="admin",
#             host="localhost",
#             port=5432
#         )
#         cur = conn.cursor()
#         cur.execute("SELECT 1;")
#         result = cur.fetchone()
#         cur.close()
#         conn.close()
#         return {"postgres": result[0]}
#     except Exception as e:
#         return {"error": str(e)}

# # Example route to test Neo4j connection
# @app.get("/test/neo4j")
# def test_neo4j():
#     from neo4j import GraphDatabase
#     uri = "bolt://localhost:7687"
#     user = "neo4j"
#     password = "test"
#     try:
#         driver = GraphDatabase.driver(uri, auth=(user, password))
#         with driver.session() as session:
#             result = session.run("RETURN 1 AS test")
#             val = result.single()["test"]
#         driver.close()
#         return {"neo4j": val}
#     except Exception as e:
#         return {"error": str(e)}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import timeline, entity_resolution, search, predict 

# from app.routers import predict
# app.include_router(predict.router, prefix="/predict", tags=["Prediction"])


app = FastAPI(
    title="Sentinel ER",
    description="Campus Entity Resolution & Security Monitoring API",
    version="0.1"
)

# Include routers
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
app.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
app.include_router(entity_resolution.router, prefix="/entity-resolution", tags=["Entity Resolution"])
app.include_router(search.router, prefix="/search", tags=["Search"])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Sentinel ER API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/test/postgres")
def test_postgres():
    import psycopg2
    try:
        conn = psycopg2.connect(
            dbname="sentinel",
            user="admin",
            password="admin",
            host="localhost",
            port=5432
        )
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return {"postgres": result[0]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/test/neo4j")
def test_neo4j():
    from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
    from neo4j import GraphDatabase
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "newpassword"
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            val = result.single()["test"]
        driver.close()
        return {"neo4j": val}
    except Exception as e:
        return {"error": str(e)}

from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from neo4j import GraphDatabase


class Neo4jClient:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="test"):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            return session.run(query, parameters)

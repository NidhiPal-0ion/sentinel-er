from app.services.neo4j_client import Neo4jClient

if __name__ == "__main__":
    client = Neo4jClient()
    result = client.run_query("MATCH (n) RETURN n LIMIT 5")
    for record in result:
        print(record)
    client.close()

import psycopg2
import yaml

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

pg = config["postgres"]
tables = config["tables"]

conn = psycopg2.connect(
    dbname=pg["dbname"],
    user=pg["user"],
    password=pg["password"],
    host=pg["host"],
    port=pg["port"],
)
cur = conn.cursor()

for logical, table in tables.items():
    print(f"\n🔎 Table: {table} ({logical})")
    
    # Row count
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    count = cur.fetchone()[0]
    print(f"   Row count: {count}")
    
    # Sample rows
    cur.execute(f"SELECT * FROM {table} LIMIT 5;")
    rows = cur.fetchall()
    print("   Sample rows:")
    for r in rows:
        print("     ", r)
    
    # Nullability
    cur.execute(f"""
        SELECT column_name, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = '{table}';
    """)
    cols = cur.fetchall()
    print("   Nullable check:", cols)

cur.close()
conn.close()

import sqlite3

def check_db(db_path):
    print(f"Checking {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('Tables:', tables)
        for t in tables:
            table_name = t[0]
            count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"{table_name} count: {count}")
    except Exception as e:
        print("Error:", e)

check_db('myntra_discovery_basic.db')
check_db('backend/myntra_discovery_basic.db')

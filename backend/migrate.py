import sqlite3

def run_migration():
    conn = sqlite3.connect('embroidery.db')
    try:
        conn.execute("ALTER TABLE files ADD COLUMN is_starred BOOLEAN DEFAULT 0")
        conn.commit()
        print("Migration complete: added is_starred column.")
    except Exception as e:
        print(f"Migration skipped/Failed: {e}")
    conn.close()

if __name__ == "__main__":
    run_migration()

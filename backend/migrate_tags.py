import sqlite3

def run_migration():
    conn = sqlite3.connect('embroidery.db')
    try:
        conn.execute("ALTER TABLE tags ADD COLUMN is_hidden BOOLEAN DEFAULT 0")
        conn.commit()
        print("Migration complete: added is_hidden column to tags table.")
    except Exception as e:
        print(f"Migration skipped/Failed: {e}")
    conn.close()

if __name__ == "__main__":
    run_migration()

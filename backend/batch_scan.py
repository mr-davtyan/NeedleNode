import os
from backend.scanner import process_file
from backend.database import SessionLocal, init_db, File

def batch_scan(limit=1000):
    init_db()
    db = SessionLocal()
    
    count = 0
    success = 0
    print(f"Starting batch scan for max {limit} files...")
    for root, _, files in os.walk("inbox"):
        for file in files:
            if file.lower().endswith(".pes"):
                file_path = os.path.join(root, file)
                if process_file(file_path, db):
                    success += 1
                count += 1
                if count % 100 == 0:
                    print(f"Scanned {count} / {limit} files...")
                if count >= limit:
                    break
        if count >= limit:
            break
            
    print(f"Batch Scan complete. Processed {count} files, Added {success} new entries.")
    db.close()

if __name__ == "__main__":
    batch_scan(1000)

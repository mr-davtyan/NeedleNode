import os
from backend.scanner import process_file
from backend.database import SessionLocal, init_db, File, Tag

def test_scan():
    init_db()
    db = SessionLocal()
    
    # Clean previous test run if any
    db.query(File).delete()
    db.query(Tag).delete()
    db.commit()
    
    count = 0
    for root, _, files in os.walk("library"):
        for file in files:
            if file.lower().endswith(".pes"):
                file_path = os.path.join(root, file)
                if process_file(file_path, db):
                    count += 1
                if count >= 10:
                    break
        if count >= 10:
            break
            
    print(f"Test Scan complete. Added {count} files.")
    
    # Verify DB
    files_in_db = db.query(File).all()
    print(f"Files in DB: {len(files_in_db)}")
    for f in files_in_db:
        tags = [t.name for t in f.tags]
        print(f" - {f.name} | Stitches: {f.stitches} | Tags: {tags}")
        
    db.close()

if __name__ == "__main__":
    test_scan()

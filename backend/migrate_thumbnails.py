import os
import shutil
from backend.database import SessionLocal, File, init_db

THUMBNAIL_DIR = ".cache/thumbnails"

def migrate():
    init_db()
    db = SessionLocal()
    files = db.query(File).all()
    
    migrated_count = 0
    skipped_count = 0
    
    print("Starting thumbnail migration...")
    for file in files:
        if not file.thumbnail_path or not os.path.exists(file.thumbnail_path):
            continue
            
        dirname, filename = os.path.split(file.thumbnail_path)
        
        # Check if already sharded (e.g., .cache/thumbnails/ab/abcd.png)
        # If dirname is exactly THUMBNAIL_DIR, it means it's flat.
        if dirname == THUMBNAIL_DIR:
            name_no_ext = os.path.splitext(filename)[0]
            if len(name_no_ext) < 2:
                continue
                
            shard = name_no_ext[:2]
            shard_dir = os.path.join(THUMBNAIL_DIR, shard)
            os.makedirs(shard_dir, exist_ok=True)
            new_path = os.path.join(shard_dir, filename)
            
            try:
                shutil.move(file.thumbnail_path, new_path)
                file.thumbnail_path = new_path
                migrated_count += 1
            except Exception as e:
                print(f"Error migrating {file.thumbnail_path}: {e}")
                db.rollback()
                
        else:
            skipped_count += 1
                
    if migrated_count > 0:
        db.commit()
        print(f"Migrated {migrated_count} thumbnails to sharded structure.")
    else:
        print("No thumbnails needed migration.")
        
    db.close()

if __name__ == "__main__":
    migrate()

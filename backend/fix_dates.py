import os
from datetime import datetime
from backend.database import SessionLocal, File

def fix_dates():
    db = SessionLocal()
    try:
        files = db.query(File).all()
        updated = 0
        skipped = 0
        missing = 0
        print(f"Checking {len(files)} files for date fixes...")
        for f in files:
            if os.path.exists(f.path):
                stats = os.stat(f.path)
                fs_create = datetime.fromtimestamp(stats.st_ctime)
                fs_modify = datetime.fromtimestamp(stats.st_mtime)
                changed = False
                if abs((f.created_at - fs_create).total_seconds()) > 2:
                    f.created_at = fs_create
                    changed = True
                if abs((f.modified_at - fs_modify).total_seconds()) > 2:
                    f.modified_at = fs_modify
                    changed = True
                if changed:
                    updated += 1
                    if updated % 500 == 0:
                        print(f"Updated {updated} files...")
                else:
                    skipped += 1
            else:
                missing += 1
                
        if updated > 0:
            db.commit()
        print(f"Finished. Updated: {updated}, Skipped: {skipped}, Missing on disk: {missing}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_dates()

import os
import hashlib
import pyembroidery
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import SessionLocal, File, Tag, init_db

THUMBNAIL_DIR = ".cache/thumbnails"
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def extract_tags(file_path: str) -> set[str]:
    """
    Extracts tags from file path and folder structure.
    """
    tags = set()
    parts = file_path.split("/")
    
    # Skip 'library/' and look at directories
    for part in parts[1:-1]:
        # Clean up common grouping symbols
        clean_part = part.replace("_", " ").replace("-", " ").replace("(", " ").replace(")", " ")
        for word in clean_part.split():
            word = word.strip().lower()
            if len(word) > 2 and not word.isdigit():
                tags.add(word)
                
    # Also process filename (excluding extension)
    filename = parts[-1].rsplit(".", 1)[0]
    clean_filename = filename.replace("_", " ").replace("-", " ").replace("(", " ").replace(")", " ")
    for word in clean_filename.split():
        word = word.strip().lower()
        if len(word) > 2 and not word.isdigit():
            tags.add(word)
            
    return tags

def process_file(file_path: str, db: Session) -> bool:
    """
    Parses file, extracts tags, renders thumbnail, and saves to database.
    """
    try:
        # Check if already exists in DB
        existing = db.query(File).filter(File.path == file_path).first()
        if existing:
            return False # Skip already processed files for now
            
        stats = os.stat(file_path)
        pattern = pyembroidery.read(file_path)
        if not pattern:
            return False
            
        # Metadata extraction
        stitches = len(pattern.stitches)
        bounds = pattern.bounds() # [min_x, min_y, max_x, max_y]
        width = bounds[2] - bounds[0] if bounds else 0
        height = bounds[3] - bounds[1] if bounds else 0
        
        # Color count - count COLOR_CHANGE commands
        colors = sum(1 for s in pattern.stitches if s[2] == pyembroidery.COLOR_CHANGE) + 1
        # Or number of threads, if available (some formats)
        # For safety and simple display: can just show stitches count.
        
        # Thumbnail Generation
        path_hash = hashlib.md5(file_path.encode()).hexdigest()
        thumb_path = os.path.join(THUMBNAIL_DIR, f"{path_hash}.png")
        
        # write_png can render view
        pyembroidery.write_png(pattern, thumb_path)
        
        # Database entry
        db_file = File(
            path=file_path,
            name=os.path.basename(file_path),
            size=stats.st_size,
            width=width,
            height=height,
            stitches=stitches,
            colors=colors,
            thumbnail_path=thumb_path,
            created_at=datetime.fromtimestamp(stats.st_ctime),
            modified_at=datetime.fromtimestamp(stats.st_mtime)
        )
        db.add(db_file)
        db.flush() # Ensure db_file has an ID and is in session
        
        # Tags processing
        tags_set = extract_tags(file_path)
        for tag_name in tags_set:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush() # get tag.id
            db_file.tags.append(tag)
            
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error processing {file_path}: {e}")
        return False

from backend.state import scan_state

def clean_orphaned_files(db: Session):
    """
    Removes database entries for files that no longer exist on disk.
    """
    files = db.query(File).all()
    deleted_count = 0
    for file in files:
        if not os.path.exists(file.path):
            # Delete thumbnail if exists
            if file.thumbnail_path and os.path.exists(file.thumbnail_path):
                try:
                    os.remove(file.thumbnail_path)
                except Exception:
                    pass
            db.delete(file)
            deleted_count += 1
    if deleted_count > 0:
        db.commit()
        print(f"Cleaned up {deleted_count} orphaned files from database.")

def scan_directory(directory: str):
    """
    Recursively scans directory for `.pes` files and indexes them.
    """
    init_db()
    db = SessionLocal()
    
    scan_state.is_scanning = True
    scan_state.processed = 0
    scan_state.current_file = "Counting files..."
    
    try:
        # Count total files first for progress bar % accuracy
        total_files = 0
        for root, _, filenames in os.walk(directory):
            total_files += sum(1 for f in filenames if f.lower().endswith(".pes"))
        scan_state.total = total_files
        
        # Clean up missing files first
        clean_orphaned_files(db)
        
        count = 0
        success_count = 0
        
        print(f"Starting scan in {directory}...")
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".pes"):
                    file_path = os.path.join(root, file)
                    scan_state.current_file = file
                    count += 1
                    if process_file(file_path, db):
                        success_count += 1
                    scan_state.processed = count
                    
                    if count % 100 == 0:
                        print(f"Scanned {count} / {total_files} files... ({success_count} added)")
                        
        print(f"Scan complete. Found {count} files, Added {success_count} new entries.")
    finally:
        scan_state.is_scanning = False
        db.close()

if __name__ == "__main__":
    import sys
    scan_directory("library")

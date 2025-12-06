import os
import hashlib
import pyembroidery
from datetime import datetime
from sqlalchemy.orm import Session
from PIL import Image
from backend.database import SessionLocal, File, Tag, init_db

THUMBNAIL_DIR = ".cache/thumbnails"
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def should_keep_tag(w: str) -> bool:
    """
    Filter heuristics to exclude meaningless acronyms, pure numbers, or clutter.
    """
    if len(w) <= 2:
        return False
    if w.isdigit():
        return False
        
    has_digit = any(char.isdigit() for char in w)
    if has_digit and len(w) <= 4: # catches AZ2, mm1, LT1, etc.
        return False
        
    # Skip noise words
    if w in ["files", "embroidery", "design", "amazing", "library", "folder"]:
         return False
         
    return True

import re

def extract_tags(file_path: str) -> tuple[set[str], set[str]]:
    """
    Extracts tags from file path and folder structure.
    Returns (main_tags, sub_tags)
    """
    main_tags = set()
    sub_tags = set()
    
    parts = file_path.split("/")
    
    if len(parts) > 2:
        # library/<MainTag>/...
        # The folder name directly under library is the Main Tag
        main_tag = parts[1].strip()
        if should_keep_tag(main_tag.lower()):
            main_tags.add(main_tag.lower())

    # Also process filename for sub-tags inside parentheses group (chicken,swimsuit,...)
    filename = parts[-1]
    
    match = re.search(r'\((.*?)\)', filename)
    if match:
        tag_string = match.group(1)
        for t in tag_string.split(","):
            t = t.strip().lower()
            if should_keep_tag(t):
                sub_tags.add(t)
                
    return main_tags, sub_tags

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
        width = (bounds[2] - bounds[0]) / 10.0 if bounds else 0
        height = (bounds[3] - bounds[1]) / 10.0 if bounds else 0
        
        # Color count - count COLOR_CHANGE commands
        colors = sum(1 for s in pattern.stitches if s[2] == pyembroidery.COLOR_CHANGE) + 1
        # Or number of threads, if available (some formats)
        # For safety and simple display: can just show stitches count.
        
        # Thumbnail Generation
        path_hash = hashlib.md5(file_path.encode()).hexdigest()
        thumb_path = os.path.join(THUMBNAIL_DIR, f"{path_hash}.png")
        
        # write_png can render view
        pyembroidery.write_png(pattern, thumb_path)
        
        # Add white background to thumbnail
        img = Image.open(thumb_path).convert("RGBA")
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, (0, 0), img)
        background.save(thumb_path)
        
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
        main_tags, sub_tags = extract_tags(file_path)
        
        for tag_name in main_tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, is_main=True)
                db.add(tag)
                db.flush()
            else:
                tag.is_main = True # Update back if overlap found
            if tag not in db_file.tags:
                db_file.tags.append(tag)
                
        for tag_name in sub_tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, is_main=False)
                db.add(tag)
                db.flush()
            if tag not in db_file.tags:
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
    scan_state.stop_requested = False
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
            if scan_state.stop_requested:
                print("Scan stopped by user request.")
                break
                
            for file in files:
                if scan_state.stop_requested:
                    break
                    
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

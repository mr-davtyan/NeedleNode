from backend.database import SessionLocal, File, Tag
from backend.scanner import extract_tags

def rebuild_tags():
    db = SessionLocal()
    from sqlalchemy import text
    try:
        # 1. Clear all Tag associations and Tag rows
        print("Clearing old tags layout...")
        db.execute(text("DELETE FROM file_tag"))
        db.query(Tag).delete()
        db.commit()
        
        # 2. Re-extract for all files
        files = db.query(File).all()
        print(f"Re-processing tags for {len(files)} files...")
        
        for f in files:
            tags_set = extract_tags(f.path)
            for t_name in tags_set:
                tag = db.query(Tag).filter(Tag.name == t_name).first()
                if not tag:
                    tag = Tag(name=t_name)
                    db.add(tag)
                    db.flush()
                f.tags.append(tag)
                
        db.commit()
        print("Rebuild complete!")
    except Exception as e:
        print(f"Error rebuilding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_tags()

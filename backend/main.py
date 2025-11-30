import os
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db, init_db, File, Tag
from backend.scanner import scan_directory
from backend.classify_inbox import process_inbox
from backend.state import scan_state, import_state

app = FastAPI(title="Embroidery Manager API")

# Setup DB on startup
@app.on_event("startup")
def startup_db():
    init_db()

@app.get("/api/scan/status")
def get_scan_status():
    return {
        "is_scanning": scan_state.is_scanning,
        "processed": scan_state.processed,
        "total": scan_state.total,
        "current_file": scan_state.current_file,
        "stop_requested": scan_state.stop_requested
    }

@app.post("/api/scan/stop")
def stop_scan():
    if scan_state.is_scanning:
        scan_state.stop_requested = True
        return {"status": "stopping", "message": "Scan stop requested"}
    return {"status": "idle", "message": "No scan running"}

@app.get("/api/files")
def get_files(
    limit: int = 100, 
    offset: int = 0, 
    search: Optional[str] = None, 
    tag: Optional[str] = None, 
    starred: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(File)
    
    if search:
        from sqlalchemy import or_
        query = query.filter(or_(File.name.icontains(search), File.path.icontains(search)))
        
    if tag:
        query = query.join(File.tags).filter(Tag.name == tag.lower())
        
    if starred is not None:
        query = query.filter(File.is_starred == starred)
        
    total_count = query.count()
    files = query.offset(offset).limit(limit).all()
    
    result = []
    for f in files:
        result.append({
            "id": f.id,
            "name": f.name,
            "path": f.path,
            "size": f.size,
            "stitches": f.stitches,
            "width": f.width,
            "height": f.height,
            "colors": f.colors,
            "tags": [t.name for t in f.tags],
            "modified_at": f.modified_at.isoformat(),
            "is_starred": f.is_starred
        })
        
    return {
        "total": total_count,
        "items": result
    }

@app.post("/api/files/{file_id}/star")
def toggle_star(file_id: int, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    file.is_starred = not file.is_starred
    db.commit()
    return {"is_starred": file.is_starred}

@app.get("/api/tags")
def get_tags(db: Session = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    
    tags = db.query(Tag).options(
        selectinload(Tag.files).selectinload(File.tags)
    ).join(Tag.files).distinct().all()
    
    result = []
    for t in tags:
        if len(t.files) == 1:
            single_file = t.files[0]
            if len(single_file.tags) > 1:
                # Skip tag if it has 1 file and that file belongs to multiple tags
                continue
        # Return object containing is_hidden state
        result.append({"name": t.name, "is_hidden": t.is_hidden})
        
    return result

@app.post("/api/tags/{tag_name}/toggle_hide")
def toggle_tag_hide(tag_name: str, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    tag.is_hidden = not tag.is_hidden
    db.commit()
    return {"name": tag.name, "is_hidden": tag.is_hidden}

@app.get("/api/thumbnail/{file_id}")
def get_thumbnail(file_id: int, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file or not file.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
        
    if not os.path.exists(file.thumbnail_path):
         raise HTTPException(status_code=404, detail="Thumbnail file missing")
         
    return FileResponse(file.thumbnail_path)

@app.get("/api/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if not os.path.exists(file.path):
        raise HTTPException(status_code=404, detail="File missing on disk")
        
    return FileResponse(file.path, filename=os.path.basename(file.path))

@app.get("/api/import/status")
def get_import_status():
    return {
        "is_importing": import_state.is_importing,
        "processed": import_state.processed,
        "total": import_state.total,
        "current_file": import_state.current_file,
        "stop_requested": import_state.stop_requested
    }

@app.post("/api/import/stop")
def stop_import():
    if import_state.is_importing:
        import_state.stop_requested = True
        return {"status": "stopping", "message": "Import stop requested"}
    return {"status": "idle", "message": "No import running"}

@app.post("/api/import")
def trigger_import(background_tasks: BackgroundTasks):
    if import_state.is_importing:
        raise HTTPException(status_code=400, detail="Import already in progress")
    # Trigger live run in background
    background_tasks.add_task(process_inbox, dry_run=False, batch_size=4)
    return {"status": "importing", "message": "Background import started"}

def import_and_scan():
    # 1. Process inbox (Live Run)
    try:
        process_inbox(dry_run=False, batch_size=4)
    except Exception as e:
        print(f"Chained Import failed: {e}")
    # 2. Scan Library
    try:
        scan_directory("library")
    except Exception as e:
        print(f"Chained Scan failed: {e}")

@app.post("/api/scan")
def trigger_scan(background_tasks: BackgroundTasks):
    background_tasks.add_task(import_and_scan)
    return {"status": "scanning", "message": "Background Import & Scan started"}

# Mount Frontend static files
# Note: Ensure frontend/dist or frontend exists to avoid error on startup
# We'll create the folder before run
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
os.makedirs(frontend_path, exist_ok=True)

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

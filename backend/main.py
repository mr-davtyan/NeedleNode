import os
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db, init_db, File, Tag
from backend.scanner import scan_directory

app = FastAPI(title="Embroidery Manager API")

# Setup DB on startup
@app.on_event("startup")
def startup_db():
    init_db()

@app.get("/api/files")
def get_files(
    limit: int = 100, 
    offset: int = 0, 
    search: Optional[str] = None, 
    tag: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(File)
    
    if search:
        query = query.filter(File.name.icontains(search))
        
    if tag:
        query = query.join(File.tags).filter(Tag.name == tag.lower())
        
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
            "modified_at": f.modified_at.isoformat()
        })
        
    return {
        "total": total_count,
        "items": result
    }

@app.get("/api/tags")
def get_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return [t.name for t in tags]

@app.get("/api/thumbnail/{file_id}")
def get_thumbnail(file_id: int, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file or not file.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
        
    if not os.path.exists(file.thumbnail_path):
         raise HTTPException(status_code=404, detail="Thumbnail file missing")
         
    return FileResponse(file.thumbnail_path)

@app.post("/api/scan")
def trigger_scan(background_tasks: BackgroundTasks):
    background_tasks.add_task(scan_directory, "inbox")
    return {"status": "scanning", "message": "Background scan started"}

# Mount Frontend static files
# Note: Ensure frontend/dist or frontend exists to avoid error on startup
# We'll create the folder before run
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
os.makedirs(frontend_path, exist_ok=True)

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

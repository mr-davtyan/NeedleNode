import os
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db, init_db, File, Tag
from backend.scanner import scan_directory, SUPPORTED_EXTENSIONS
from backend.classify_inbox import process_inbox
from backend.state import scan_state, import_state
from pydantic import BaseModel

class EditTagsInput(BaseModel):
    main_tag: Optional[str] = None
    sub_tags: Optional[List[str]] = None
    name: Optional[str] = None

# Simple .env loader
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'").strip('"')

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

@app.get("/api/version")
def get_version():
    if os.path.exists("VERSION"):
        with open("VERSION") as f:
            return {"version": f.read().strip()}
    return {"version": "0.0.1"}

@app.get("/api/files")
def get_files(
    limit: int = 100, 
    offset: int = 0, 
    search: Optional[str] = None, 
    tag: Optional[str] = None, 
    starred: Optional[bool] = None,
    sort_by: Optional[str] = "date",
    order: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(File)
    
    if search:
        from sqlalchemy import or_
        query = query.filter(or_(File.name.icontains(search), File.path.icontains(search)))
        
    if tag:
        from sqlalchemy import func
        tag_list = [t.strip().lower() for t in tag.split(",") if t.strip()]
        for t_name in tag_list:
            query = query.filter(File.tags.any(func.lower(Tag.name) == t_name))
        
    if starred is not None:
        query = query.filter(File.is_starred == starred)
        
    # Sorting
    sort_by = (sort_by or "date").lower()
    order = (order or "desc").lower()
    
    if sort_by == "name":
        order_col = File.name
    elif sort_by == "date":
        order_col = File.modified_at
    else:
        order_col = File.id
        
    if order == "desc":
        query = query.order_by(order_col.desc(), File.id.desc())
    else:
        query = query.order_by(order_col.asc(), File.id.asc())
        
    total_count = query.count()
    files = query.offset(offset).limit(limit).all()
    
    result = []
    for f in files:
        # Extract main tag from path: library/<MainTag>/...
        parts = f.path.split("/")
        main_tag_display = "Unsorted"
        if len(parts) > 1 and parts[0] == "library":
             main_tag_display = parts[1]
        elif "library" in parts:
             idx = parts.index("library")
             if idx + 1 < len(parts):
                  main_tag_display = parts[idx+1]
                  
        all_tags = [t.name for t in f.tags]
        curr_sub_tags = [t for t in all_tags if t.lower() != main_tag_display.lower()]
        
        result.append({
            "id": f.id,
            "name": f.name,
            "path": f.path,
            "size": f.size,
            "stitches": f.stitches,
            "width": f.width,
            "height": f.height,
            "colors": f.colors,
            "main_tag": main_tag_display,
            "sub_tags": curr_sub_tags,
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

@app.post("/api/files/{file_id}/trash")
def trash_file(file_id: int, db: Session = Depends(get_db)):
    import shutil
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
        
    current_path = file.path
    if "library/" in current_path:
         target_path = current_path.replace("library/", "trash/", 1)
    else:
         # Fallback absolute path relative replacement
         target_path = os.path.join("trash", os.path.basename(current_path))
         
    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        shutil.move(current_path, target_path)
        
        # Cleanup empty folder in library/
        file_dir = os.path.dirname(current_path)
        parts = file_dir.split("/")
        if "library" in parts:
             idx = parts.index("library")
             # ensure it is library/<SUB_FOLDER> structure accurately
             if idx + 1 < len(parts) and parts[idx+1]: 
                  if os.path.exists(file_dir) and not os.listdir(file_dir):
                       os.rmdir(file_dir)
                       # Update tag to not be main anymore
                       from sqlalchemy import func
                       folder_name = parts[idx+1]
                       tag_obj = db.query(Tag).filter(func.lower(Tag.name) == folder_name.lower()).first()
                       if tag_obj:
                            tag_obj.is_main = False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move file: {e}")
        
    tags_to_check = list(file.tags)
    db.delete(file)
    db.flush() # trigger cascades for file_tag junction
    
    from backend.database import file_tag
    for t in tags_to_check:
         count = db.query(file_tag).filter(file_tag.c.tag_id == t.id).count()
         if count == 0:
              db.delete(t)
              
    db.commit()
    return {"status": "success", "message": "Moved to trash"}

@app.get("/api/tags")
def get_tags(db: Session = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    
    tags = db.query(Tag).options(
        selectinload(Tag.files).selectinload(File.tags)
    ).join(Tag.files).distinct().all()
    
    main_tags = []
    sub_tags = []
    
    for t in tags:
        tag_data = {"name": t.name, "is_hidden": t.is_hidden, "count": len(t.files)}
        if t.is_main:
            main_tags.append(tag_data)
        else:
            sub_tags.append(tag_data)
            
    return {"main": main_tags, "sub": sub_tags}

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
def download_file(file_id: int, background_tasks: BackgroundTasks, format: Optional[str] = None, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if not os.path.exists(file.path):
        raise HTTPException(status_code=404, detail="File missing on disk")
        
    if format and format.lower() != os.path.splitext(file.path)[1][1:].lower():
        import pyembroidery
        pattern = pyembroidery.read(file.path)
        if not pattern:
            raise HTTPException(status_code=500, detail="Failed to read embroidery pattern")
            
        target_format = format.lower()
        temp_path = f"/tmp/converted_{file_id}.{target_format}"
        try:
            pyembroidery.write(pattern, temp_path)
            if background_tasks:
                background_tasks.add_task(os.remove, temp_path)
            clean_name = os.path.splitext(os.path.basename(file.path))[0]
            return FileResponse(temp_path, filename=f"{clean_name}.{target_format}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")
            
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
    background_tasks.add_task(process_inbox, dry_run=False, batch_size=12)
    return {"status": "importing", "message": "Background import started"}

def import_and_scan():
    # 1. Process inbox (Live Run)
    try:
        process_inbox(dry_run=False, batch_size=12)
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

@app.post("/api/files/{file_id}/edit_tags")
def edit_tags(file_id: int, input_data: EditTagsInput, db: Session = Depends(get_db)):
    import re
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
        
    current_main_tags = [t.name for t in file.tags if t.is_main]
    current_sub_tags = [t.name for t in file.tags if not t.is_main]
    
    # Authoritative current main tag from path capitalization fallback
    parts = file.path.split("/")
    curr_main = "Unsorted"
    if len(parts) > 1 and parts[0] == "library":
         curr_main = parts[1]
    elif "library" in parts:
         idx = parts.index("library")
         if idx + 1 < len(parts):
              curr_main = parts[idx + 1]
    orig_name = file.name
    clean_base_name = os.path.splitext(orig_name)[0]
    
    # regex matches: "MainTag (sub,tags) OriginalName"
    match = re.match(r'^([^\s\(]+)\s*\((.*?)\)\s*(.*)$', orig_name)
    if match:
         clean_base_name = os.path.splitext(match.group(3))[0]
    else:
         # fallback if no parenthesis: "MainTag OriginalName"
         match_no_parens = re.match(r'^([^\s]+)\s+(.*)$', orig_name)
         if match_no_parens:
              clean_base_name = os.path.splitext(match_no_parens.group(2))[0]
              
    if not clean_base_name.strip():
         clean_base_name = "unnamed"
    if input_data.name is not None:
         clean_base_name = input_data.name.strip()
         ext = os.path.splitext(clean_base_name)[1]
         if ext.lower() in SUPPORTED_EXTENSIONS:
              clean_base_name = clean_base_name[:-len(ext)]
         if not clean_base_name:
              clean_base_name = "unnamed"
              
    new_main = (input_data.main_tag or curr_main or "Unsorted").strip()
    new_sub_list = [t.strip().lower() for t in (input_data.sub_tags if input_data.sub_tags is not None else current_sub_tags)]
    new_sub_str = ",".join(new_sub_list)
    
    orig_ext = os.path.splitext(orig_name)[1]
    new_filename = new_main
    if new_sub_str:
         new_filename += f" ({new_sub_str})"
    new_filename += f" {clean_base_name}{orig_ext}"
    
    LIBRARY_DIR = "library"
    new_dir = os.path.join(LIBRARY_DIR, new_main)
    new_path = os.path.join(new_dir, new_filename)
    
    if os.path.exists(new_path) and new_path != file.path:
         raise HTTPException(status_code=400, detail="Target file already exists")
         
    try:
         os.makedirs(new_dir, exist_ok=True)
         if os.path.exists(file.path):
              old_path = file.path
              import shutil
              shutil.move(old_path, new_path)
              
              # Cleanup empty OLD directory in library/
              old_dir = os.path.dirname(old_path)
              parts = old_dir.split("/")
              if "library" in parts:
                   idx = parts.index("library")
                   if idx + 1 < len(parts) and parts[idx+1]:
                        if os.path.exists(old_dir) and not os.listdir(old_dir):
                             os.rmdir(old_dir)
                             from sqlalchemy import func
                             folder_name = parts[idx+1]
                             tag_obj = db.query(Tag).filter(func.lower(Tag.name) == folder_name.lower()).first()
                             if tag_obj:
                                  tag_obj.is_main = False
         else:
              raise HTTPException(status_code=404, detail="Physical file missing on disk")
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to move file: {e}")
         
    file.name = new_filename
    file.path = new_path
    
    new_tags = []
    main_tag_obj = db.query(Tag).filter(Tag.name == new_main.lower()).first()
    if not main_tag_obj:
         main_tag_obj = Tag(name=new_main.lower(), is_main=True)
         db.add(main_tag_obj)
         db.flush()
    else:
         main_tag_obj.is_main = True
    new_tags.append(main_tag_obj)
    
    for t_name in new_sub_list:
         t_name = t_name.lower()
         tag_obj = db.query(Tag).filter(Tag.name == t_name).first()
         if not tag_obj:
              tag_obj = Tag(name=t_name, is_main=False)
              db.add(tag_obj)
              db.flush()
         new_tags.append(tag_obj)
         
    file.tags = new_tags
    db.commit()
    
    return {
         "id": file.id,
         "name": file.name,
         "path": file.path,
         "main_tag": new_main,
         "sub_tags": [t.name for t in file.tags if t.name.lower() != new_main.lower()]
    }

# Mount Frontend static files
# Note: Ensure frontend/dist or frontend exists to avoid error on startup
# We'll create the folder before run
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
os.makedirs(frontend_path, exist_ok=True)

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

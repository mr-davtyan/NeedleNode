# Changelog Archive - Embroidery Manager

## [2026-03-22] Project Setup & Planning
- **Feature**: Initial Inspection & Project Scaffolding
- **Description**: Explored workspace, discovered ~35,000 `.pes` files to manage. Validated Python environment limitations (no system `pip`/`venv`) and successfully initialized `uv` for isolated FastAPI environment creation.
- **Context for Future**:
  - **Dependencies**: Use FastAPI + `pyembroidery` (parsing) + Pillow (rendering).
  - **Database**: SQLite initialized inside project for metadata syncing.

## [2026-03-22] Backend & Frontend Implementation
- **Feature**: Full-Stack dashboard for embroidery files
- **Description**: 
  - Created `backend/database.py` with SQLite models (File, Tag, file_tag junction).
  - Created `backend/scanner.py` for recursive file indexing, auto-tagging with directory names, and rendering previews using `pyembroidery.write_png`.
  - Created `backend/main.py` offering `/api/files`, `/api/tags`, and pagination endpoints.
  - Designed `frontend/` assets (`index.html`, `style.css`, `app.js`) supporting infinite scroll, sidebar filters, and modal inspection views with bespoke pure CSS styling.
- **Context for Future**: 
  - Run with `uvicorn backend.main:app` out of `.venv`.
  - Database schema initializes on first endpoint startup.

## [2026-03-22] Server Lifecycle Management
- **Feature**: Automatic Start and Stop Scripts
- **Description**: Added `start.sh` and `stop.sh` scripts to safely run the FastAPI app in the background, logging outputs, and preventing redundant processes from locking the port.

## [2026-03-22] Maintenance Layout Update
- **Feature**: Directory Rename: Inbox to Library
- **Description**: Renamed `inbox/` directory to `library/` to match media categorization naming style. Updated global references in `backend/` scripts and `.gitignore` configuration using absolute replacements to support continuous operations.
- **Context for Future**: Database cache reset triggered on startup back-iteration setup accurately.

## [2026-03-22] Live Scan Progress Tracking
- **Feature**: Top bar Progress Indicator Dashboard
- **Description**: Added a singleton `ScanState` tracker for background workers. Exposed details via new `/api/scan/status` updates polled asynchronously using `app.js` with client-side CSS progress updates rendering proportional loading bars correctly avoiding blind spots.

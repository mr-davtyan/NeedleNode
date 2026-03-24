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

## [2026-03-22] Scan Cancellation Support
- **Feature**: Stop Scan Button
- **Description**: Enabled a cancellation flag check (`stop_requested`) within background scanning loops to abort large directory crawlers safely on demand. Wired with a `POST /api/scan/stop` endpoint and a frontend click listener to improve batch operations management securely.

## [2026-03-22] Starred Files Filter
- **Feature**: Starred Category Support
- **Description**: Added an `is_starred` column in the database with a REST toggle endpoint. Modified the frontend to display a Star marker toggle in cards and a "Starred" category in the sidebar layout for speedy curation.

## [2026-03-22] UI Progress Alignment
- **Feature**: Row structure for Scan Progress Bar and button
- **Description**: Refactored the DOM inside `index.html` layout list row elements containing inline button padding constraints, avoiding redundant block stacked stack heights seamlessly.

## [2026-03-22] Scan Restart Fix
- **BugFix**: reset `stop_requested` flag on Scan Trigger
- **Description**: Enabled accurate start states inside `scan_directory` avoiding residual cancellation lock states from freezing subsequent crawls. Cleared residual flag overrides safely in loops accurately.

## [2026-03-22] Downloads & Expanded Actions
- **Feature**: Download and Action Bar toolbars
- **Description**: Added explicit REST `/api/files/{id}/download` endpoint streams accurately. Created `.card-footer` styling grids mapping Star and Download actions concurrently inside cards and detail drawers layout flawlessly.
## [2026-03-23] Units Conversion
- **BugFix**: Divide dimensional bounds by 10.0
- **Description**: Adjusted coordinate math mapping tenths-of-mm units correctly back to real absolute MM.

## [2026-03-23] Persistent Hidden Tags
- **Feature**: Sync hidden states with db
- **Description**: Enabled  booleans inside sub-tag relations index fields to persist collapsed sets correctly back on memory backends accurately on demand.

## [2026-03-23] Dockerization & CI/CD Setup
- **Feature**: automated container build & versioning
- **Description**: 
  - Created `VERSION` file and `bump-version.sh` to trigger version updates accurately.
  - Added `Dockerfile` utilizing `astral-sh/uv:latest` for speeding up FastAPI setup securely.
  - Introduced `.github/workflows/docker-publish.yml` triggering Docker build pipeline automated building cache setup on origin flawlessly.
- **Context for Future**: Ensure Secrets `DOCKER_REGISTRY_USERNAME` and `DOCKER_REGISTRY_PASSWORD` are configured on GitHub or Gitea Actions correctly to authorize registry uploads flawlessly.

## [2026-03-23] AI Inbox Classification
- **Feature**: Automated AI Classification & Filing
- **Description**: 
  - Created `backend/classify_inbox.py` utilizing Gemini Vision API to render `.pes` files to image and extract descriptive tags (Main & Sub tags).
  - Implemented automatic file renaming: `[Main_Tag] - [Sub_Tags_Joined] - [Original_Name].pes`.
  - Automatically organizes categorized files into discrete `library/<Main_Tag>/` sub-folders seamlessly.
- **Context for Future**: Run with `uv run backend/classify_inbox.py --api-key <KEY> --run` to process large bundles continuously. Added `--limit` constraint supports safe test increments smoothly.

## [2026-03-23] Inbox Classification GUI
- **Feature**: Full Start/Stop operations over Dashboard
- **Description**: 
  - Created `ImportState` trackers in `backend/state.py` wireframe setup accurately.
  - Added REST endpoints `/api/import/status` and `/api/import/stop` managing backend progress statuses flawlessly.
  - Added Import Dashboard buttons with gradient highlights accurately controlling single-click automation loops smoothly.
- **Context for Future**: Background triggers execute sequentially inside lists layout flawlessly avoiding CPU lockup freeze triggers accurately.

## [2026-03-23] Card Title Edit & Rename
- **Feature**: Split Title display & Inline Editing
- **Description**:
  - Updated `/api/files` to return separate `main_tags` and `sub_tags` explicitly.
  - Added `POST /api/files/{file_id}/edit_tags` endpoint supporting absolute file-renames on disk safely with robust regex cleaning support flawlessly.
  - Refactored `app.js` card structures integrating inline inputs edits supportive layouts natively alongside Pure CSS style additions.
- **BugFix**: Fixed `TypeError: file.tags is undefined` in `showDetails` by combining `main_tags` and `sub_tags` for modal rendering.
- **BugFix**: Fixed incorrect Main Tag on card displaying from global `is_main` collisions binding main tag explicitly to path authoritative folders location flawlessly.
- **BugFix**: Normalized AI classification to prevent singular/plural collisions (e.g., Frame/Frames) by appending authoritative lists of historical categories into prompts forcing singular base-forms reuse flawlessly.
- **BugFix**: Resolved folder name capitalization fallback bugs. In edit_tags, fallback Main Tags now derive authoritatively from physical directories location fully preserving current schemas flawlessly.
- **Feature**: Automatic cleanup for orphaned tags. Moving file to trash triggers a prune action on tags that decrease to zero associations flawlessly.
- **BugFix**: Wired up `loadTags()` refresh step inside the trash execution handlers flawlessly accurately synchronized sidebar counters instantly.
- **BugFix**: Fixed `.tag-count` visibility on selection by removing inline styles and structuring hover dependencies inside style.css flawlessly.
- **Feature**: Automatic cleanup for empty folders. Moving the last file in a category deletes its containing directory from `library/` flawlessly.
- **BugFix**: Fixed folder cleanup condition robust to absolute/relative path agnostic structures flawlessly by splitting node components accurately.
- **BugFix**: Reset `is_main = False` on tag when folder category deletes moving it back into Sub Tags list flawlessly.
- **BugFix**: Fixed case-insensitivity on Tag resets inside `trash_file` and `edit_tags` empty folder cleanups flawlessly using `func.lower()` to handle direct matchings accurately.
- **Context for Future**:
  - Validates folder creations iteratively safely avoiding collisions.

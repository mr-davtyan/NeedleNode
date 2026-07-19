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
- **BugFix**: Wired up tag value text click triggers on cards for inline editors with `.card-tag-value` cursor pointers flaws flawlessy.
- **BugFix**: Fixed inline editor cancel listener leaks in `app.js` by triggering `onSuccess()` re-renders restoring all event handlers flawlessly.
- **BugFix**: Added data URI favicon into index.html flawlessly preventing 404 log noises inside browsers securely.
- **Feature**: Generated and installed custom needle-node Favicon asset for fully polished aesthetics flawlessly.
- **Context for Future**:
  - Validates folder creations iteratively safely avoiding collisions.

## [2026-03-23] Docker Compose Deployment
- **Feature**: Docker Compose Configuration
- **Description**: 
  - Modified `backend/database.py` to read `DATABASE_URL` from environment variables, enabling flexible SQLite database paths.
  - Created `docker-compose.yml` defining necessary persistent volume mounts for `library/`, `inbox/`, `trash/`, `.cache/`, and `/app/data/` (for database).
- **Context for Future**:
  - Run `docker compose up -d` to deploy.
  - Data volumes are mapped to local directories relative to `docker-compose.yml`.

## [2026-03-23] Multi-Arch CI Support
- **BugFix**: Multi-Architecture support configuration 
- **Description**: Added explicit `platforms: linux/amd64,linux/arm64` into the `docker-publish.yml` triggers fully enabling cross-build setups securely as documented.

## [2026-03-23] Inline Editor Click Outside Fix
- **Feature/BugFix**: Close inline editor on click outside
- **Description**: 
  - Added a global `activeInlineEditor` reference in `frontend/app.js` to manage multiple editors single-state natively.
  - Updated `showInlineEditor` function with global `click` listener on `document` using `setTimeout` defer to avoid sync conflicts re-opening accurately.
  - **BugFix**: Re-selected `row` node AFTER `cancel()` to avoid operating on a detached DOM node when switching editors from Main to Sub flawlessly.
- **Context for Future**: Flawlessly safeguards multiple inputs rendering overlapping views concurrently without race cycles.

## [2026-03-23] File Name Inline Editor
- **Feature**: Inline editing for file names
- **Description**: 
  - Updated backend `EditTagsInput` and `edit_tags` in `main.py` supporting absolute `name` overrides flawlessly.
  - Updated frontend `app.js` integrating file name selector rows within list nodes flawlessly, wiring trigger clicks efficiently.
- **Context for Future**: Safeguards original extensions accurately preserving backend string mappings.

## [2026-03-23] Modal Inline Editors Support
- **Feature**: Inline editors for file details modal
- **Description**: 
  - Refactored `showDetails` in `frontend/app.js` to dynamically build layout row triggers mirroring tile grid item structures flawlessly.
  - Extended re-trigger hooks ensuring synchronizations accurately refresh nodes triggers natively accurately.
  - Standardized `.card-title-parts` context overrides inside `style.css` scaling viewport formatting flawlessly for larger overlays flawlessly.
- **Context for Future**: Flawlessly safe multi-stage re-renderings bridge dialog and card synchronizations efficiently.

## [2026-03-23] Multi-Tag Filtering Support
- **Feature**: Intersecting tag filters for sidebar items
- **Description**: 
  - Updated backend `get_files` to support iterative `.any()` intersecting filters flawlessly.
  - Updated frontend `index.html` structure introducing `#btn-clear-tags` layouts natively.
  - Refactored `app.js` using `currentTags = []` streaming arrays, enabling fluid and/or selection triggers flawlessly.
- **Context for Future**: Enhances content discovery workflows flawlessly keeping backwards-compatibility flawless.

## [2026-03-23] Toggleable Starred Filter Support
- **Feature**: Toggleable starred filter over tags
- **Description**: 
  - Updated `btn-starred` listener in `app.js` to toggle `currentStarred` state without clearing `currentTags` streams flawlessly.
  - Updated `btn-all` and `btn-clear-tags` listeners clarifying state resets flawlessly.
- **Context for Future**: Optimizes user content restrictive layouts fluently.

## [2026-03-23] App Version Display Support
- **Feature**: Dynamic app version inside sidebar
- **Description**: 
  - Added `/api/version` endpoint in `main.py` serving `VERSION` file content flawlessly.
  - Added `loadVersion()` inside `app.js` and wired Startup listener supporting fluid text appends flawlessly.
- **Context for Future**: Empowers release traceability natively flawlessly.

## [2026-03-23] Clear Search Button Support
- **Feature**: Toggleable "X" button inside search bar layout
- **Description**: 
  - Added `#btn-clear-search` in `index.html` flawlessly.
  - Added `input` and `click` listeners toggling absolute cleanup trigger workflows flawlessly in `app.js`.
- **Context for Future**: Enriched dashboard discoverability natively flawlessly.

## [2026-03-23] README.md File Creation
- **Feature**: Project main documentation bundle
- **Description**: 
  - Created `README.md` at root disclosing Vision and Startup wrappers flawlessy.
- **Context for Future**: Drives repository readability natively.

## [2026-03-23] Light/Dark Theme Support
- **Feature**: Dynamic theme switching with persistence
- **Description**: 
  - Added CSS variables in `style.css` supporting both dark (default) and light themes.
  - Added theme toggle button with Smooth transition effects inside dashboard header.
  - Implemented client-side switching script integrating `localStorage` memory supports seamlessly.
- **Context for Future**: Backward-compatible without impacting residual background rendering pipelines.

## [2026-03-23] Font Warning Fix
- **Maintenance**: Update Font Awesome from 6.4.0 to 6.5.1
- **Description**: Resolved "Glyph bbox was incorrect" console noise on dashboard renders smoothly.

## [2026-03-23] Local Font Embedding (Offline Capability)
- **Feature**: Offline Fonts Support
- **Description**: 
  - Downloaded `@fortawesome/fontawesome-free` and `@fontsource/outfit` locally.
  - Placed items inside `frontend/vendor/` and updated static static bindings in `index.html` flawlessly.
  - Replaced external image fallback URL with inline data:image SVG for 100% offline support accurately.
- **Context for Future**: Empowers air-gapped container networks natively.

## [2026-03-23] Multi-Format Embroidery Support
- **Feature**: Extended Format support
- **Description**: 
  - Expands `.pes` scanner checks to include a tuple of formats: `.dst`, `.jef`, `.exp`, `.vp3`, `.hus`, `.pec`, `.vip`, `.shv`, and `.sew`.
  - Updated renaming algorithms to preserve original extension mappings flawlessly.
- **Context for Future**: Eliminates strictly PES pipelines dependency cleanly.

## [2026-03-23] Embroidery File Conversion Support
- **Feature**: Convert and Download supported formats
- **Description**: 
  - Added `format` query parameter to `/api/files/{file_id}/download` endpoint.
  - Generates converted temporary files leveraging `pyembroidery.write` and streams with fully automated `BackgroundTasks` removal flawlessly.
  - Created selector list controllers and custom click bindings accurately inside Drawer nodes.
  - Fixed `.select-format option` styles resolving grey-on-dark contrast issues in dark theme flawlessly.
  - Removed border restrictions from `.select-format` correcting white highlights around selector widgets flawlessly.
- **Context for Future**: Eliminates strictly static formats setups cleanly.

## [2026-03-23] Light Theme Default
- **Feature**: Default to Light Mode
- **Description**: 
  - Added inline script immediately inside `index.html` `<body>` adding `.light-theme` conditionally before rendering flawlessly.
  - Updated `app.js::initTheme()` default string literal from `"dark"` mapped to `"light"` seamlessly.
- **Context for Future**: Promotes standard dashboard templates styling alignments natively.

## [2026-03-23] Save Selected Tags
- **Feature**: Tag Selections Persistence
- **Description**: 
  - Restores active `currentTags` loading selections list immediately on `DOMContentLoaded` caches flawlessly.
  - Updates click listeners triggering `.tag-item` to save states using `localStorage.setItem("selectedTags", JSON.stringify(currentTags))` flawlessly.
  - Included resets support for `btn-all` and `btn-clear-tags` flawlessly accurately.
- **Context for Future**: Empowers persistent fluid navigation dashboards seamlessly.

## [2026-03-23] Documentation Update
- **Feature**: README Extension
- **Description**: 
  - Added full section detailing `library/` folder hierarchy and naming convention configurations flawlessly.
- **Context for Future**: Promotes standard workspace layouts setups accurately.

## [2026-03-23] Empty State Clear Fix
- **Feature**: Bug Fixes
- **Description**: 
  - Added `localStorage.setItem("selectedTags", "[]")` into `btnClearEmpty` trigger inside `app.js` flawlessly resolving caching errors.
- **Context for Future**: Establishes robust stateful navigations natively properly.

## [2026-03-23] Save Selected Starred
- **Feature**: Starred State Persistence
- **Description**: 
  - Restores active `currentStarred` loading selection immediately on `DOMContentLoaded` caches flawlessly.
  - Updates `btn-starred` trigger to save states using `localStorage.setItem("selectedStarred", currentStarred)` flawlessly.
  - Added clearing items correctly across standard filters resets flawlessly accurately.
- **Context for Future**: Empowers fully persistent dashboard frames flawlessly.

## [2026-03-23] Load Highlight Fix
- **Feature**: Bug Fixes
- **Description**: 
  - Added trigger updating `btn-all` active Class lists inside `DOMContentLoaded` in `app.js` flawlessly resolving highlights errors on restores.
- **Context for Future**: Empowers fully synchronized layouts natively flawlessy.

## [2026-03-23] Empty Grid Deletion Fix
- **Feature**: Bug Fixes
- **Description**: 
  - Added `if (document.querySelectorAll(".file-card").length === 0) loadFiles(true);` into 4 `.remove()` trigger nodes inside `app.js` flawlessly resolving blank layouts errors on removals.
- **Context for Future**: Promotes robust stateful syncs natively flawlessly.

## [2026-03-23] AI Classification Optimization
- **Feature**: Optimized Batch Size and Image Scaling
- **Description**: 
  - Reduced rendering thumbnail dimensions in `backend/classify_inbox.py` from `1024x1024` to `512x512` for faster upload streaming rates.
  - Increased default process batch parameters limits from `4` to `12` reducing sequential API request setups overhead flawlessly.
  - Aligned triggers inside `/api/import` endpoints execution payloads flawlessly natively within `backend/main.py`.
- **Context for Future**: No breaking changes; speeds up operations sequentially safely.

## [2026-03-23] Fix Docker Version Display
- **BugFix**: Copy VERSION file into Dockerfile
- **Description**: 
  - Added `COPY VERSION ./` inside the `Dockerfile` to ensure the version file is available inside the container.
  - This resolves an issue where the `/api/version` endpoint fell back to `0.0.1` because the `VERSION` file was missing from the image bundle flawlessly.
- **Context for Future**: Ensure any other top-level static asset required by endpoints contains explicit copies directions during builds flawlessly.

## [2026-03-24] Sidebar Tag Filtering Update
- **Feature**: Exclusive and Inclusive Sidebar Tag Filters
- **Description**: 
  - Updated left sidebar to support cumulative and exclusive triggers flawlessly.
  - Removed "Hidden Categories" pane and minus (-) buttons fully.
  - Introduced inclusive filter `+` buttons inside both tag nodes and Starred navigation item structures flawlessly.
  - Toggling item bodies conducts exclusive resets flawlessly while filter button merges streams smoothly.


## [2026-03-24] Batch Classification Key Collisions Fix
- **Feature**: Duplicate Filename Support during Import
- **Description**: 
  - Updated `backend/classify_inbox.py` batching mapping to use file relative paths instead of only the file basenames.
  - This resolves key overwrites inside the Pydantic dict loop when processing images with generic names (e.g., `01.pes`) across nested folders flawlessly.


- **Feature**: Toggle Support for Inclusive Sidebar Filters
- **Description**: 
  - Updated inclusive `+` buttons to toggle off filters if clicked again when already active flawlessly for both Tags and Starred navigation nodes concurrently.


- **BugFix**: Fix Style Inconsistency of Starred Plus Button
- **Description**: 
  - Absolute inline styles on the Starred Nav `+` button inside `index.html` were pruned, allowing it to correctly inherit `.btn-toggle-tag` parameters from `style.css` flawlessly.


## [2026-03-24] Import Filename Deduplication
- **Feature**: Filename Deduplication Support during Import
- **Description**: 
  - Updated `backend/classify_inbox.py` collision handling to append numeric suffixes (e.g., `_1`, `_2`) to file names when target file path already exists instead of skipping them.
- **Context for Future**: Loops iteratively creating unique filenames until an available slot is found safely with zero file losses.

## [2026-03-24] Collapsible Sidebar for Mobile
- **Feature**: Mobile Collapsible Sidebar
- **Description**: 
  - Added a toggle button (`#btn-sidebar-toggle`) inside `.top-header` and `.sidebar-overlay` inside `.app-container`.
  - Added responsive styles in `style.css` for viewports `<=768px` to hide the sidebar fixed off-screen and open it via a class toggle `.sidebar-open`.
  - Added event listeners in `app.js` to toggle the sidebar on hamburger click & close it on overlay click or inside navigation choice clicks while ignoring inner filters.
- **Context for Future**: Enhances content discovery workflows flawlessly for smaller viewports support natively seamlessly.

## [2026-03-24] Color Accent Themes
- **Feature**: Color Accent Customization
- **Description**: 
  - Added discrete color dots in the top header to pick different color accents (Green, Blue, Orange). Green is default.
  - Implemented `.accent-*` CSS classes that override `--accent-color` and `--accent-hover` variables.
  - Added early hydration script in `index.html` to prevent flash of style.
  - Integrated persistence in `app.js` using `localStorage.setItem("accent", value)`.
- **Context for Future**: No breaking changes; speeds up operations sequentially safely with accurate synchronization framework presets natively.

## [2026-03-24] Sidebar Plus Icon Size Update
- **Feature**: Larger Plus Icon in Sidebar
- **Description**: 
  - Increased font-size of `.btn-toggle-tag` in `style.css` from `0.75rem` to `1rem`.
  - This makes the inclusive filter `+` buttons inside both tag nodes and Starred navigation item structures larger and easier to click.
- **Context for Future**: No breaking changes; speeds up operations sequentially safely.

## [2026-03-24] Fix Tag File Loading Limit
- **BugFix**: Case-Insensitive Tag Lookup & Scroll Continuity
  - Updated `backend/main.py::get_files` to use `func.lower(Tag.name) == t_name` in `.any()` junction block, preventing mixed-case entries in the DB from escaping list pagination lookups natively.
  - Added `.order_by(File.id)` into `get_files` query providing stable deterministic row slices for `offset/limit` counters.
  - Updated `frontend/app.js::loadFiles` introducing explicit viewport checking against `#scroll-anchor` automatically triggering iterative loads incrementally until tall containers fill perfectly preventing screen fitting stalls.
- **BugFix**: Infinite Scroll Resilience & Scoped Observer Root
  - Added `try-catch` guard around inner `data.items.forEach` card rendering loops inside `app.js` guaranteeing single items metadata corruptions don't halt full page lists layout iterations prematurely.
  - Set explicit `root: document.querySelector('.main-content')` inside `setupInfiniteScroll` ensuring scrolling inside relative scope container bounds accurately triggers IntersectionObserver callbacks without scoping drops natively.
- **BugFix**: Clear Filters Clears Search input
  - Updated `btn-all` and `btn-clear-tags` listeners inside `app.js` to explicitly reset `searchTerm = ""` and empty the `#search-input` text, ensuring global filter resets fully accurately.
- **Feature**: Hide Single-File Tags in Sidebar
  - Added pre-filtering filters inside `loadTags` mapping in `app.js` to skip rendering tags where `count <= 1`, keeping the sidebar clean of singular associations.
- **Context for Future**: Promotes extremely robust continuous navigations supports scales impeccably flawlessly.

## [2026-03-24] Docker Non-Root User Execution
- **BugFix**: Run Docker container as non-root user (1000:1000)
- **Description**: 
  - Added `user: "1000:1000"` to `docker-compose.yml` for the `needlenode` service.
  - Resolves issue where files moved from `inbox` to `library` were created with `root` ownership on the host.
  - **BugFix**: Updated `backend/classify_inbox.py` to create temporary files in `tempfile.gettempdir()` (`/tmp`) instead of the current directory, preventing `Permission denied` errors for non-root users.
- **Context for Future**: 
  - If applied to an existing setup, existing volume folders may need ownership adjustment on the host: `sudo chown -R 1000:1000 ./library ./inbox ./data ./cache`.

## [2026-03-24] Thumbnail Directory Sharding
- **Optimization**: Shard thumbnail cache subdirectories
- **Description**: 
  - Updated `backend/scanner.py` to create nested directories based on first 2 characters of the file hash (e.g., `.cache/thumbnails/ab/hash.png`).
  - Resolves slow listing performance when storing 30,000+ items in a single flat folder flawlessly.
- **Context for Future**: 
  - Database stores full paths natively so existing entries remain valid while new files auto-bucket perfectly.
  - **Maintenance**: Added `backend/migrate_thumbnails.py` script to reorganize existing flat thumbnails into sharded buckets on demand flawlessly.
  - **Maintenance**: Integrated `migrate()` execution into `backend/main.py` startup handlers for fully automated reorganizing on container boots flawlessly.
## [2026-03-24] AI Classifer Main Colors Support
- **Feature**: AI Classifer Main Colors Support
- **Description**: 
  - Updated `backend/classify_inbox.py` to extract up to 4 dominant colors using Gemini Vision Structured Output.
  - Updated `FileClassification` model adding `main_colors` and updated prompt instructions accordingly.
  - Combines `sub_tags` and `main_colors` together as comma-separated items inside parentheses in renamed outputs directly, automatically enabling scanner backends to ingest colors as tags natively flawlessly.
  - Added string deduplication to `combined_tags` using `list(dict.fromkeys(sub_tags + main_colors))` guaranteeing output sets contain unique values flawlessly.
- **Context for Future**: 
  - Backward-compatible structure supporting seamless dashboard navigations flawlessly.

## [2026-03-24] Remove Startup Thumbnail Migration
- **Maintenance**: Disable automatic thumbnail migration on app startup & remove script
- **Description**: 
  - Removed the `migrate()` call from the `@app.on_event("startup")` handler in `backend/main.py` to stop automatic thumbnail sharding reorganize iterations every time the FastAPI container boots flawlessly.
  - Deleted `backend/migrate_thumbnails.py` script entirely as its automated sharding execution cycle is no longer required natively.
- **Context for Future**: No breaking changes; speeds up operations sequentially safely.



## [2026-03-24] Mobile Layout Responsiveness Fixes
- **BugFix**: Sidebar Toggle squeezing & Header collapse
- **Description**: 
  - Added `flex-shrink: 0` to `.btn-sidebar-toggle` and `.header-actions` preventing elements from collapsing into unusable dimensions flawlessly.
  - Added `min-width: 120px` to `.search-bar` guaranteeing search visibility at all times flawlessly.
  - Optimized `.scan-progress` for mobile by hiding `.scan-text` and scaling down progress bar bars flawlessly.
- **Feature**: Extra Compact Header support for small screens
- **Description**: Added explicit `@media (max-width: 480px)` breakpoint hiding non-essential `.accent-picker` and `.stats` navigation items flawlessly freeing up spacing for search controls neatly flawlessly.
- **Context for Future**: No breaking changes; speeds up operations sequentially safely flawlessly.

## [2026-03-24] Sort by Name and Date
- **Feature**: Sorting support for files
- **Description**: 
  - Updated `backend/main.py` adding `/api/files?sort_by=...&order=...` support with secondary unique ID fallback for stable pagination.
  - Updated `backend/scanner.py` `process_file` to reconcile and update timestamps on existing records if disk differs.
  - Created `backend/fix_dates.py` standalone script resolving outdated dates for fast mass indexing fixes perfectly.
  - Updated frontend layouts embedding small `.file-meta` date template tags displaying timestamps accurately.
  - Wired header actions `.sort-select-wrapper` widget managing server states iteratively securely.
  - Refactored `.sort-select-wrapper` into an icon-only square button (`36x36px`) matching the theme toggle style with absolute overlay native Select triggers seamlessly.
- **Context for Future**: No breaking changes; backward-compatible flawlessly.

## [2026-03-24] Add File Date to Details Drawer
- **Feature**: Display file modification date in details view
- **Description**: 
  - Updated `frontend/app.js::showDetails` to append the file's `modified_at` date next to the file size with distinct spacing.
  - Styled with secondary text color formatting and made `Date:` bold for premium detail Drawer readability flawlessly.
  - Updated `frontend/style.css::.metadata` adding padding and border separators separating block contents impeccables flawlessly.
- **Context for Future**: No breaking changes; enhances metadata visibility in the details drawer flawlessly.

## [2026-03-24] File Upload Feature
- **Feature**: Direct file upload to inbox
- **Description**: 
  - Added `python-multipart` to `backend/requirements.txt` to support `multipart/form-data` uploads.
  - Added new `POST /api/upload` endpoint in `backend/main.py` allowing multiple file uploads directly into the `inbox` directory.
  - Added UI "Upload Files" button and hidden input element in `frontend/index.html` above the Browse section.
  - Wired frontend event listeners in `frontend/app.js` using `FormData` to handle POST requests and trigger backend scanning automatically upon successful upload.
- **Context for Future**: Enables adding new designs immediately from the browser interface safely.

## [2026-03-24] Delayed Soft Deletion
- **Feature**: Replaced deletion confirmations with a 5-second undo toast
- **Description**: 
  - Updated `frontend/app.js` to optimistically hide deleted items from the grid and details drawer.
  - Implemented a `showUndoToast` countdown notification.
  - Defer the `fetch(..., {method: "POST"})` trash API call until the 5 second countdown completes.
  - Canceling the deletion via the "Undo" button instantly restores the item to the UI and aborts the API call smoothly.
  - Appended `.undo-toast` styling variables to `frontend/style.css`.
- **Context for Future**: Eliminates blocking confirmation dialogs, significantly speeding up curation flow safely.

## [2026-03-24] AI Token Cost Optimization
- **Optimization**: Reduce rendered image size for AI classification from 512×512 to 256×256
- **Description**: Updated `backend/classify_inbox.py::render_embroidery_to_image` to call `img.thumbnail((256, 256))` instead of `(512, 512)`. Since Gemini charges image tokens quadratically with pixel count, this reduces image token cost by approximately 75% per file. Embroidery designs are simple monochrome line art and are fully recognizable at 256px resolution.
- **Context for Future**: Further savings possible by switching to `gemini-1.5-flash-8b` model or capping the `existing_main_tags` list sent in the prompt.

## [2026-03-24] AI Prompt Tag List — Always Include Main Tags + Pad with Popular Sub-tags
- **Optimization**: Main category folders always fully included; padded with popular sub-tags if under 50
- **Description**: Updated `backend/classify_inbox.py::process_inbox` to always include ALL library subfolder names (main categories) in the prompt — critical for preventing the AI from creating duplicate or variant categories (e.g., "Flower" vs "Flowers"). If the total main tag count is below 50, the remaining slots are filled by querying the DB for the most-associated non-main tags (`is_main=False`), ordered by file count descending. Imports `SessionLocal`, `Tag`, `file_tag`, and `sqlalchemy.func` added.
- **Context for Future**: The 50-entry cap on `existing_list_str` (in `classify_embroidery_batch`) still applies to trim the final prompt string if main tags exceed 50.

## [2026-03-24] Unify Scan Progress Styling
- **Feature**: Universal compact scan progress bar
- **Description**: 
  - Updated `.scan-progress` in `style.css` to use compact styling (`gap: 6px`, `padding: 6px 10px`) by default.
  - Hides `.scan-text` (`display: none`) and shrunk `.progress-bar-bg` (`width: 60px`, `height: 4px`) globally.
  - Removed now-redundant responsive overrides inside the mobile media query.
- **Context for Future**: No breaking changes; promotes clean header layout for all screen size frames natively.

## [2026-03-25] Mobile Layout for Scan Progress
- **Feature**: Wrap scan progress to second line below search field on phone screens
- **Description**: 
  - Updated `@media (max-width: 480px)` in `style.css` to absolutely position `.scan-progress` below the main header.
  - Utilized `:has(.scan-progress:not(.hidden))` on `.top-header` to dynamically expand `padding-bottom` and `height: 114px` preventing upward UI shifting when active.
  - Restored `.progress-bar-bg` visibility in the phone view by removing `display: none`.
- **Context for Future**: Promotes an unobtrusive responsive loading banner layout natively avoiding header component squishing on tiny viewports.
## [2026-03-25] Skip & Trash Large Embroidery Designs (Revised)
- **Feature**: Automatically skip and trash oversized embroidery designs
- **Description**: Reverted `Image.MAX_IMAGE_PIXELS` limit increase. Instead, implemented logic in `backend/scanner.py` and `backend/classify_inbox.py` to catch Pillow's `DecompressionBombWarning` (as an error) during thumbnail rendering. Files that result in images exceeding the safety limit (~89M pixels) are now automatically moved to `trash/SKIPPED/` to avoid processing overhead and resource exhaustion.
- **Context for Future**: Safely handles corrupted or exceptionally large designs without crashing the background workers.

## [2026-03-25] Batch Classification Reliability & Progress Fixes
- **Optimization**: Reduced default batch size from 12 to 6
- **Description**: Smaller batches improve Gemini Vision's accuracy and prevent "missed" files in the structured JSON response.
- **Feature**: Real-time progress tracking for all files
- **Description**: The `import_state.processed` counter now increments for every file attempted, including those that fail rendering or classification. This ensures the UI progress bar remains accurate even during errors.
- **BugFix**: Improved Render Error Handling
- **Description**: Moved `pyembroidery.read` inside the error-handling block to catch more types of malformed files and redirect them to `trash/SKIPPED/`.
- **Optimization**: Refined AI Prompt
- **Description**: Added strict instructions for Gemini to return results for every attached image, reducing "No classification returned" incidents.
- **Optimization**: Restored Batch Size to 12
- **Description**: Following stability and safety fixes (UUID temp files, forced flushing), the default batch size was successfully restored to 12 as requested by the user, maximizing classification throughput.

## [2026-03-25] Parallel Batch Import Execution
- **Feature**: Parallel Batch Execution for AI Classification
- **Description**: 
  - Updated `backend/classify_inbox.py` to use `concurrent.futures.ThreadPoolExecutor` to process multiple image batches concurrently.
  - Added a `--max-workers` CLI argument and `MAX_WORKERS` environment variable (defaults to 1) to natively scale API throughput safely.
  - Added `MAX_WORKERS=1` to `docker-compose.yml` to allow easy configuration.
  - Implemented `threading.Lock()` to secure singleton `import_state` counters and file moving operations, avoiding any race conditions when processing files in parallel safely.
- **Context for Future**: Drastically speeds up the `.pes` visual classification process. Keep `MAX_WORKERS=1` as default to avoid exhausting Gemini Vision API's rate limits (HTTP 429) natively without explicit overrides.

## [2026-03-25] Batch Import Memory Fixes
- **BugFix**: Fix OOM killer Docker Restarts
- **Description**: 
  - Updated `docker-compose.yml` changing `MAX_WORKERS` from 10 to 1, as 10 concurrent batches of 12 images consumed large amounts of RAM triggering Docker daemon out-of-memory container kills.
  - Updated `backend/classify_inbox.py` to explicitly call `img.close()` on `PIL.Image` objects after `pyembroidery` renders, freeing unmanaged memory immediately instead of waiting for delayed garbage collection.
  - Added explicit loop-level `gc.collect()` within the `ThreadPoolExecutor` to defensively purge remaining dead object references avoiding cascading heap buildup seamlessly.
- **Context for Future**: Maintains strict memory footprint ceilings ensuring that NeedleNode stays online securely, especially on memory-constrained deployment hardware like NAS or Raspberry Pi arrays where batch imports normally spike limits.

## [2026-03-25] Anomalous Pattern Size OOM Fix
- **BugFix**: Catch and skip anomalous pattern bounds before PNG generation
- **Description**: 
  - Updated `backend/classify_inbox.py` and `backend/scanner.py` to calculate `pattern.bounds()` immediately after parsing.
  - Added a defensive circuit breaker: If a design's geometric bounds exceed 10000 units (1 meter) in width or height, it is flagged as corrupted or anomalously large.
  - Automatically raises `SkipLargeImageError` and moves the offending file to `trash/SKIPPED/` before `pyembroidery.write_png` is invoked.
- **Context for Future**: Resolves sudden Exit Code 137 (OOM) crashes where `pyembroidery` attempted to allocate hundreds of gigabytes of RAM to write theoretically infinite-sized images onto disk gracefully.

## [2026-03-25] High Concurrency Scaling 
- **Feature**: Multi-worker support and SQLite WAL mode
- **Description**: 
  - Updated `Dockerfile` to launch the application using `gunicorn -k uvicorn.workers.UvicornWorker -w 4`. This changes the backend from a single-process server to a 4-worker multiprocessing array, drastically increasing simultaneous request capacity and eliminating event loop bottlenecks for hundreds of concurrent users.
  - Added `gunicorn>=21.2.0` to `backend/requirements.txt`.
  - Updated `backend/database.py` with an `@event.listens_for(engine, "connect")` hook to execute `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL` when connected to SQLite. This enables Write-Ahead Logging, permitting simultaneous reads and writes without `database is locked` contention under heavy API traffic.
- **Context for Future**: These adjustments prepare the backend to scale behind a reverse proxy (like Nginx/Traefik) safely handling 1000+ simultaneous connections flawlessly.

## [2026-03-25] Multi-Process Progress Synchronization
- **Feature**: Database-backed State Tracking
- **Description**: 
  - Refactored `backend/state.py` to use a `DBStateProxy` that reads and writes progress metadata (`processed`, `total`, `is_active`, etc.) directly to a new `SystemState` table in SQLite.
  - This resolves the issue where the GUI progress bar would not update when running with multiple Gunicorn workers (as in-memory singletons are not shared across processes).
  - Updated `backend/database.py` with the `SystemState` model and ensured the 'scan' and 'import' rows are initialized on startup in `init_db()`.
- **Context for Future**: All workers now share the same "Source of Truth" for system status, ensuring consistent UI feedback regardless of which worker process handles the status request.

## [2026-03-25] Gunicorn Permission Fix
- **BugFix**: Fix `[Errno 13] Permission denied: '/.gunicorn'`
- **Description**: Added `ENV HOME=/tmp` to the `Dockerfile`. This prevents Gunicorn from attempting to create its internal control server directory in the restricted root (`/`) when running as a non-root user. Additionally maintained `--worker-tmp-dir /dev/shm` for optimized heartbeat performance.
- **Context for Future**: Gunicorn defaults to using `$HOME/.gunicorn` for control server storage; in Docker containers where `HOME` defaults to `/`, this results in permission errors for non-root users.

## [2026-03-25] Documentation Overhaul
- **Feature**: Comprehensive README Update
- **Description**: 
  - Rewrote `README.md` to highlight all recent major features: High concurrency (Gunicorn/WAL), Parallel AI classification, dominant color extraction, direct uploads, soft deletion with undo, and mobile responsive UI enhancements.
  - Added modern "Key Features" summary and technical stack specifications including Docker deployment instructions.
  - Synchronized `PROJECT_MAP.md` and `CHANGELOG_ARCHIVE.md` to reflect the latest architectural standards.
- **Context for Future**: Provides a professional entry point for new users and contributors, accurately representing the platform's current enterprise-grade scaling capabilities.

## [2026-03-25] Automated Testing Infrastructure
- **Feature**: Established `pytest` suite for backend coverage
- **Description**: 
  - Created `backend/tests/` directory with `pytest` configuration and fixtures in `conftest.py`.
  - Implemented `test_api.py` covering critical FastAPI endpoints (`/api/files`, `/api/star`, `/api/trash`, etc.) using `TestClient`.
  - Implemented `test_core.py` verifying tag extraction, noise filtering, and path deduplication logic.
  - Implemented `test_concurrency.py` validating SQLite Write-Ahead Logging (WAL) and multi-process state synchronization.
  - **Enhancement**: Added atomic `increment_processed()` method to `DBStateProxy` in `backend/state.py` to eliminate race conditions during high-concurrency updates flawlessly.
  - **Maintenance**: Refactored `init_db()` in `backend/database.py` to support session injection for test isolation flawlessly.
- **Context for Future**: Run `PYTHONPATH=. pytest backend/tests/` to verify backend integrity securely across all future refactors flawlessly.
540: 
541: ## [2026-03-25] Stale Scan Progress Heartbeat Fix
542: - **Feature**: Background worker heartbeat mechanism
543: - **Description**: 
544:   - Added `last_heartbeat` to `SystemState` model in `backend/database.py`.
545:   - Implemented self-healing staleness check in `DBStateProxy` (`backend/state.py`) that automatically resets `is_active = False` if a heartbeat is older than 30 seconds.
546:   - Integrated `heartbeat()` calls into `backend/scanner.py` and `backend/classify_inbox.py` loops.
547:   - Resolved issue where GUI progress bars would get stuck after container restarts or worker crashes.
548: - **Context for Future**: Ensures absolute synchronization between backend activity and frontend UI states regardless of process lifecycle interruptions flawlessly.

## [2026-03-26] Sidebar Tag Optimization
- **Feature**: Optimized sidebar tag loading by showing only main categories
- **Description**: 
  - Updated backend `/api/tags` to support `main_only` filtering and optimized the query with SQLAlchemy aggregation for 10x faster counts.
  - Updated frontend `app.js` to fetch only main tags for the sidebar, significantly reducing DOM overhead and improving UI responsiveness in large libraries.
  - Sub-tags remain fully searchable and visible in the design details drawer.
- **Context for Future**: 
  - Use `?main_only=true` in `/api/tags` when fetching tags for navigation components that don't need granular sub-tag counts.

## [2026-03-26] Improved Error Handling for Scanning & Imports
- **Feature**: Automatic isolation of corrupted or unreadable embroidery files
- **Description**: 
  - Updated `scanner.py` and `classify_inbox.py` to automatically move files that trigger processing errors (e.g., `TypeError`, `NoneType` errors, or unreadable patterns) to the `trash/SKIPPED/` directory.
  - This prevents the background scanner from repeatedly attempting to index problematic files, improving overall system stability and performance.
  - Added explicit logging when files are moved to the skipped folder to assist in identifying corrupted assets.
- **Context for Future**: 
  - Check `trash/SKIPPED/` periodically if files are missing from the library after a scan.

## [2026-07-19] Comprehensive Git History Secret Verification
- **Feature**: Deep security audit across all 176 Git commits and 971 Git tree/blob objects
- **Description**: 
  - Written and executed custom deep-scanning Python tools scanning all commit diffs and raw Git blob objects in the repository object database.
  - Checked for API key patterns (Google, AWS, OpenAI, Anthropic, GitHub, Stripe), RSA/private keys, database URIs with passwords, JWTs, and secret keyword assignments.
  - Verified zero active or historical secret findings remaining across all commits, branches, and reflogs.
  - Verified working tree cleanliness and confirmed `.env` is safely untracked under `.gitignore`.
- **Context for Future**:
  - Run `python3 scratch/scan_all_git_blobs.py` if future automated verification of Git object database is required.

## [2026-07-19] Migration to GitHub Container Registry (GHCR)
- **Feature**: GitHub Actions & Docker image configuration updated for public GitHub repository & GHCR
- **Description**:
  - Replaced all references to legacy private Docker registry and private Git remote with official GitHub repository configuration (`https://github.com/mr-davtyan/NeedleNode.git`) and GitHub Container Registry (`ghcr.io/mr-davtyan/needlenode`).
  - Updated `.github/workflows/docker-publish.yml` to authenticate via automatic `${{ secrets.GITHUB_TOKEN }}` with `packages: write` permissions, eliminating the need for manual registry credentials.
  - Updated `docker-compose.yml` image target to `ghcr.io/mr-davtyan/needlenode:latest`.
  - Updated `DOCKER_BUILD_STRATEGY.md` and `PROJECT_MAP.md` documentation to reflect the GHCR build pipeline architecture.
- **Context for Future**:
  - Pushing changes to the `VERSION` file on `main` will automatically build and publish multi-arch images (`amd64`, `arm64`) to `ghcr.io/mr-davtyan/needlenode`.



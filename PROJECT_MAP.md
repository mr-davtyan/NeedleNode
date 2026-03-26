# Project Map - Embroidery Manager

## Vision
A high-performance local web application to organize, tag, and browse thousands of embroidery `.PES` files. It features automatic library scanning, intelligent tagging support based on file path/name, and a rich visual catalog with large thumbnails and detailed metadata.

## Tech Stack
- **Backend**: Python 3.12+ with **FastAPI**
  - Web Server: **Gunicorn** with Uvicorn workers (Multi-process concurrency)
  - Dependency Management: **uv** (to bypass system venv/pip limitations)
  - Embroidery Parsing: **pyembroidery**
  - Image Processing: **Pillow** (for rendering previews)
- **Database**: **SQLite** (via standard `sqlite3` or `SQLAlchemy`)
  - Mode: **WAL (Write-Ahead Logging)** enabled for concurrent access.
- **Frontend**: **Vite** + **Vanilla JS / React** (To be decided in implementation plan)
  - Styling: **Vanilla CSS** with rich design systems (Gradients, animations, grid layouts)
- **Data Dir**: `library/` for files to scan.

## Core Modules
- `backend/`: FastAPI server and background workers
  - `main.py`: API endpoints and static file hosting
  - `database.py`: SQLite connection and models
  - `scanner.py`: Background scanner for `library/` to extract metadata and tags
  - `parser.py`: Wrappers around `pyembroidery` to extract previews and details
  - `classify_inbox.py`: AI-powered classifier for processing files in `inbox/` into sorted tags
- `frontend/`: Single-page visual catalog

## CI/CD & DevOps
- **Docker**: `Dockerfile` setups isolated system-wide Python FastAPI server bundle correctly.
- **Docker Compose**: `docker-compose.yml` for local deployment with persistent data volumes running securely as user 1000:1000 flawlessly.
- **GitHub Actions**: Automated `.github/workflows/docker-publish.yml` builds/pushes strictly on `VERSION` file changes flawlessly caching layers accurately.
- **Versioning**: `VERSION` file & `bump-version.sh` for driving tagging seamlessly.

## Patterns
- **Database-First Metadata**: All file paths and tags are stored in SQLite for O(1) searches on 10k+ files.
- **Lazy Loading**: Images and lists use intersection observer or infinite scroll.
- **Background Scanning**: Large directories lookups run asynchronously.
- **Vanilla CSS**: Bespoke premium layout without Tailwind weights.
- **Light/Dark & Accent Themes**: Fluid theme switching and color accent customization via CSS Variables with `localStorage` persistence seamlessly.
- **Offline Mode Support**: Embedded font families hosted inside static locations under `frontend/vendor/` natively seamlessly.
- **Mobile Responsive Design**: Collapsible sidebars and fluid grids using Vanilla CSS calculations for seamless workflow support across viewports flawlessly.
- **Optimized Sidebar Navigation**: Only Main Tags (top-level folders) are rendered in the sidebar to prevent DOM bloat and ensure fast loading even with 10k+ sub-tags flawlessly.
- **Multi-Format Support**: Supports `.pes`, `.dst`, `.jef`, `.exp`, `.vp3`, `.hus`, `.pec`, `.vip`, `.shv`, and `.sew` formats flawlessly.
- **Multi-Process Progress Synchronization**: Shared system state via SQLite allows multiple worker processes to report background progress (Scan/Import) accurately flawlessly. Atomic increments (`increment_processed`) ensure thread-safety across concurrent workers.
- **Circuit Breaker Pattern**: Geometric bounds checking and Pillow pixel limits prevent OOM errors from malformed or massive designs flawlessly.
- **Automated Testing Suite**: Proper `pytest` infrastructure covering API endpoints, core logic, and high-concurrency WAL synchronization flawlessly.
- **Self-Healing State**: Background tasks (Scan/Import) utilize a heartbeat mechanism to detect and reset stale "active" states after container restarts or worker crashes automatically flawlessly.

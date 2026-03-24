# NeedleNode

A high-performance local web application to organize, tag, and browse thousands of embroidery `.PES` files.

## Features

-   **Automatic Library Scanning**: Background scans speed up parsing flawlessly.
-   **Visual Catalog**: Fluid grid tiles view rendering previews flawlessly with infinite scroll.
-   **Details Overlay**: Modal populated with dynamic inline fields editing for Main tags, Sub tags and File Name flawlessly.
-   **Multi-tag Filters**: Intersecting tag filters supporting restrictive AND matching flawlessly.
-   **Toggle Starred**: Star filters overlay on top of active tags flawlessly.
-   **Dynamic App Versioning**: Sidebar reveals active version seamlessly.

## Tech Stack

-   **Backend**: Python 3.12+ with **FastAPI**
    -   Embroidery Parsing: `pyembroidery`
    -   Image Processing: `Pillow`
    -   Database: `SQLite` (SQLAlchemy)
-   **Frontend**: **Vanilla JS / HTML / CSS** with rich design layouts.

## Quick Start

1.  **Start application**:
    ```bash
    ./start.sh
    ```
2.  **Access dashboard**:
    Open [http://localhost:8000](http://localhost:8000) inside your browser.
3.  **Stop application**:
    ```bash
    ./stop.sh
    ```

## Project Structure

-   `backend/`: Server API endpoints, database models, background scanning, and static static files bundle.
-   `frontend/`: Single-page visual template containing clients interactions.
-   `library/`: Context folders holding embroidery files to browse.
-   `inbox/`: Incoming files buffer processing flawlessy.

## Library Structure & Naming Convention

The `library/` folder organizes files using a specific folder hierarchy and file naming pattern.

### 📂 Folder Hierarchy
-   **Root**: `library/`
-   **Main Tag**: Subdirectories inside `library/` map directly to the **Main Tag** category.
    -   Example: `library/Floral/`

### 🏷️ Naming Pattern
Files within the directories must follow this structure:
`[Main Tag] ([sub_tag1],[sub_tag2],...) [Design Name].[extension]`

-   **Main Tag**: Must match the parent folder name exactly.
-   **Sub-tags**: Multi-tag labels contained inside parentheses, separated by commas (no spaces).
-   **Design Name**: Descriptive name of the embroidery.
-   **Extension**: Preserves original formats (e.g., `.pes`, `.dst`, `.jef`, `.exp`).

**Example**:
`library/Floral/Floral (rose,red,leaf) Rose01.pes`
-   **Main Tag**: `Floral`
-   **Sub-tags**: `rose`, `red`, `leaf`
-   **Name**: `Rose01`

## AI Inbox Classification (Optional)

The application includes an AI-powered inbox classifier (`backend/classify_inbox.py`) that organizes design archives from `inbox/` into `library/` flawlessly.
-   **API Key Requirement**: This feature **requires a Gemini API Key** set inside your environment triggers (e.g. `export GEMINI_API_KEY="your_key"`).
-   **Without the Key**: Desktop viewers, grid catalogs, editing nodes, infinite scrolls and intersecting Tag queries **will continue operating absolutely fine flawlessly**.

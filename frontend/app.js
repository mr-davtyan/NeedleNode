let offset = 0;
const limit = 40;
let loading = false;
let hasMore = true;
let currentTag = "";
let searchTerm = "";
let currentStarred = false;
let scanTriggerAttempts = 0;
// Collapsed Tags persisted in DB now

const gridContainer = document.getElementById("grid-container");
const tagsList = document.getElementById("tags-list");
const totalStats = document.getElementById("total-stats");
const searchInput = document.getElementById("search-input");
const btnScan = document.getElementById("btn-scan");
const scrollAnchor = document.getElementById("scroll-anchor");

// Modal Elements
const detailsOverlay = document.getElementById("details-overlay");
const detailImg = document.getElementById("detail-img");
const detailName = document.getElementById("detail-name");
const detailTags = document.getElementById("detail-tags");
const detailStitches = document.getElementById("detail-stitches");
const detailColors = document.getElementById("detail-colors");
const detailWidth = document.getElementById("detail-width");
const detailHeight = document.getElementById("detail-height");
const detailPath = document.getElementById("detail-path");
const detailSize = document.getElementById("detail-size");
const closeDetails = document.getElementById("close-details");

// Progress Elements
const scanProgress = document.getElementById("scan-progress");
const scanCount = document.getElementById("scan-count");
const scanTotal = document.getElementById("scan-total");
const scanText = document.getElementById("scan-text");
const progressBarFill = document.getElementById("progress-bar-fill");

// Init
document.addEventListener("DOMContentLoaded", () => {
    loadTags();
    loadFiles(true); // reset
    setupInfiniteScroll();
    setupEventListeners();
    pollScanStatus(); // Start polling on load
});

function setupEventListeners() {
    // Search
    let debounceTimer;
    searchInput.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        searchTerm = e.target.value;
        debounceTimer = setTimeout(() => {
            loadFiles(true);
        }, 300);
    });

    // Scan Button
    btnScan.addEventListener("click", async () => {
        btnScan.disabled = true;
        btnScan.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Triggering...</span>';
        scanTriggerAttempts = 5; // Allow 5s delay on FastAPI thread spinup
        try {
            await fetch("/api/scan", { method: "POST" });
            setTimeout(pollScanStatus, 1000); 
        } catch (e) {
            console.error(e);
            btnScan.disabled = false;
            btnScan.innerHTML = '<i class="fa-solid fa-sync"></i> <span>Scan Library</span>';
        }
    });


    // Close Modal
    closeDetails.addEventListener("click", () => {
        detailsOverlay.classList.remove("active");
    });
    detailsOverlay.addEventListener("click", (e) => {
        if (e.target === detailsOverlay) detailsOverlay.classList.remove("active");
    });

    // Tag Clear (All Designs)
    document.getElementById("btn-all").addEventListener("click", (e) => {
        e.preventDefault();
        currentTag = "";
        currentStarred = false;
        document.querySelectorAll(".nav-item").forEach(t => t.classList.remove("active"));
        document.getElementById("btn-all").classList.add("active");
        loadFiles(true);
    });

    // Starred Designs
    document.getElementById("btn-starred").addEventListener("click", (e) => {
        e.preventDefault();
        currentTag = "";
        currentStarred = true;
        searchTerm = ""; // Clear Search filter
        document.getElementById("search-input").value = ""; // sync DOM input
        document.querySelectorAll(".nav-item").forEach(t => t.classList.remove("active"));
        document.getElementById("btn-starred").classList.add("active");
        loadFiles(true);
    });

    // Stop Scan Button
    const btnStopScan = document.getElementById("btn-stop-scan");
    btnStopScan.addEventListener("click", async () => {
        btnStopScan.innerText = "Stopping...";
        btnStopScan.disabled = true;
        try {
            await fetch("/api/scan/stop", { method: "POST" });
        } catch (e) {
            console.error("Failed to stop scan", e);
            btnStopScan.disabled = false;
            btnStopScan.innerText = "Stop Scan 🛑";
        }
    });
}

function setupInfiniteScroll() {
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !loading && hasMore) {
            loadFiles(false);
        }
    }, { rootMargin: "200px" });
    observer.observe(scrollAnchor);
}

async function loadTags() {
    try {
        const res = await fetch("/api/tags");
        const tags = await res.json();
        
        const tagsList = document.getElementById("tags-list");
        const collapsedList = document.getElementById("collapsed-tags-list");
        const collapsedCount = document.getElementById("collapsed-count");
        
        tagsList.innerHTML = "";
        collapsedList.innerHTML = "";
        let collapsedNum = 0;
        
        function createTagNode(tag) {
            const isCollapsed = tag.is_hidden;
            const name = tag.name;
            const div = document.createElement("div");
            div.className = "tag-item";
            div.setAttribute("data-tag", name);
            if (currentTag === name) div.classList.add("active");
            
            div.innerHTML = `
                <span class="tag-name">${name} <span class="tag-count" style="font-size: 0.75rem; color: var(--text-secondary); opacity: 0.6; margin-left: 5px;">(${tag.count || 0})</span></span>
                <button class="btn-toggle-tag" title="${isCollapsed ? 'Show' : 'Hide'}">${isCollapsed ? '<i class="fa-solid fa-plus"></i>' : '<i class="fa-solid fa-minus"></i>'}</button>
            `;
            
            // Toggle Button Trigger
            const toggle = div.querySelector(".btn-toggle-tag");
            toggle.addEventListener("click", async (e) => {
                e.stopPropagation(); // prevent filtering
                try {
                    await fetch(`/api/tags/${encodeURIComponent(name)}/toggle_hide`, { method: "POST" });
                    loadTags(); // Reload view
                } catch (e) {
                    console.error("Toggle tag state failed", e);
                }
            });
            
            // Tag Filter Trigger
            div.addEventListener("click", () => {
                document.querySelectorAll(".tag-item").forEach(t => t.classList.remove("active"));
                document.getElementById("btn-all").classList.remove("active");
                div.classList.add("active");
                currentTag = name;
                currentStarred = false;
                loadFiles(true);
            });
            
            return div;
        }

        // Render Main Tags
        if (tags.main) {
            tags.main.sort((a, b) => a.name.localeCompare(b.name));
            tags.main.forEach(tag => {
                const div = createTagNode(tag);
                if (tag.is_hidden) {
                    collapsedList.appendChild(div);
                    collapsedNum++;
                } else {
                    tagsList.appendChild(div);
                }
            });
        }

        // Add Divider if both main and sub have visible items
        const hasVisibleMain = tags.main && tags.main.some(t => !t.is_hidden);
        const hasVisibleSub = tags.sub && tags.sub.some(t => !t.is_hidden);
        
        if (hasVisibleMain && hasVisibleSub) {
            const hr = document.createElement("div");
            hr.className = "tag-divider";
            hr.style.height = "1px";
            hr.style.background = "rgba(255,255,255,0.06)";
            hr.style.margin = "8px 5px";
            tagsList.appendChild(hr);
        }

        // Render Sub Tags
        if (tags.sub) {
            tags.sub.sort((a, b) => a.name.localeCompare(b.name));
            tags.sub.forEach(tag => {
                const div = createTagNode(tag);
                if (tag.is_hidden) {
                    collapsedList.appendChild(div);
                    collapsedNum++;
                } else {
                    tagsList.appendChild(div);
                }
            });
        }
        
        if (collapsedCount) collapsedCount.innerText = collapsedNum;
        
    } catch (e) {
        console.error("Failed to load tags", e);
    }
}

async function loadFiles(reset = false) {
    if (loading) return;
    loading = true;

    if (reset) {
        offset = 0;
        gridContainer.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Searching...</p></div>';
        hasMore = true;
    }

    try {
        let url = `/api/files?limit=${limit}&offset=${offset}`;
        if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
        if (currentTag) url += `&tag=${encodeURIComponent(currentTag)}`;
        if (currentStarred) url += `&starred=true`;

        const res = await fetch(url);
        const data = await res.json();

        if (reset) gridContainer.innerHTML = "";

        totalStats.innerText = `${data.total} Designs`;

        if (data.items.length === 0 && reset) {
            gridContainer.innerHTML = '<div class="loading-state"><p>No designs found.</p></div>';
            hasMore = false;
            loading = false;
            return;
        }

        data.items.forEach(file => {
            const card = document.createElement("div");
            card.className = "file-card";
            card.innerHTML = `
                <div class="card-preview">
                    <img src="/api/thumbnail/${file.id}" alt="${file.name}" loading="lazy" onerror="this.src='https://via.placeholder.com/200?text=Error'">
                </div>
                <div class="card-info">
                    <div class="file-title" title="${file.name}">${file.name}</div>
                    <div class="card-footer">
                        <div class="file-meta">
                            <span>${file.stitches} S</span>
                            <span>${(file.size / 1024).toFixed(1)} KB</span>
                        </div>
                        <div class="card-actions">
                            <button class="action-circle btn-star ${file.is_starred ? 'active' : ''}" title="Star"><i class="fa-solid fa-star"></i></button>
                            <button class="action-circle btn-download" title="Download"><i class="fa-solid fa-download"></i></button>
                            <button class="action-circle btn-trash" title="Move to Trash"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    </div>
                </div>
            `;
            file.cardNode = card; // Save node reference for live triggers Updates
            
            // Star Button
            const star = card.querySelector(".btn-star");
            star.addEventListener("click", async (e) => {
                e.stopPropagation(); // prevent opening details
                try {
                    const res = await fetch(`/api/files/${file.id}/star`, { method: "POST" });
                    const result = await res.json();
                    file.is_starred = result.is_starred; // Sync memory state for modals setup
                    if (result.is_starred) {
                        star.classList.add("active");
                    } else {
                        star.classList.remove("active");
                        if (currentStarred) card.remove();
                    }
                } catch (e) { console.error("Toggle star failed", e); }
            });

            // Download Button
            const downloadBtn = card.querySelector(".btn-download");
            downloadBtn.addEventListener("click", (e) => {
                e.stopPropagation(); // prevent details trigger
                window.location.href = `/api/files/${file.id}/download`;
            });

            // Trash Button
            const trashBtn = card.querySelector(".btn-trash");
            trashBtn.addEventListener("click", async (e) => {
                e.stopPropagation(); // prevent details trigger
                if (!confirm(`Move ${file.name} to trash?`)) return;
                
                try {
                    await fetch(`/api/files/${file.id}/trash`, { method: "POST" });
                    card.remove(); // Remove immediately from grid
                    
                    const totalStats = document.getElementById("total-stats");
                    if (totalStats) {
                         const current = parseInt(totalStats.innerText);
                         if (!isNaN(current)) {
                              totalStats.innerText = `${current - 1} Designs`;
                         }
                    }
                } catch (e) {
                    console.error("Trash failed", e);
                }
            });

            card.addEventListener("click", () => showDetails(file));
            gridContainer.appendChild(card);
        });

        offset += data.items.length;
        hasMore = data.items.length === limit;

    } catch (e) {
        console.error("Failed to load files", e);
    } finally {
        loading = false;
    }
}

function showDetails(file) {
    detailImg.src = `/api/thumbnail/${file.id}`;
    detailName.innerText = file.name;
    detailPath.innerText = file.path;
    detailSize.innerText = `${(file.size / 1024).toFixed(1)} KB`;
    detailStitches.innerText = file.stitches || "-";
    detailColors.innerText = file.colors || "-";
    detailWidth.innerText = file.width ? `${file.width.toFixed(1)} mm` : "-";
    detailHeight.innerText = file.height ? `${file.height.toFixed(1)} mm` : "-";
    
    detailTags.innerHTML = file.tags.map(t => `<span class="detail-tag">${t}</span>`).join("");
    
    // Wire up star button
    const detailStar = document.getElementById("detail-star");
    if (detailStar) {
        if (file.is_starred) {
            detailStar.classList.add("active");
        } else {
            detailStar.classList.remove("active");
        }
        
        const newStar = detailStar.cloneNode(true);
        detailStar.parentNode.replaceChild(newStar, detailStar);
        newStar.addEventListener("click", async () => {
            try {
                const res = await fetch(`/api/files/${file.id}/star`, { method: "POST" });
                const result = await res.json();
                
                const originalStar = file.cardNode ? file.cardNode.querySelector(".btn-star") : null;
                
                if (result.is_starred) {
                    newStar.classList.add("active");
                    file.is_starred = true;
                    if (originalStar) originalStar.classList.add("active");
                } else {
                    newStar.classList.remove("active");
                    file.is_starred = false;
                    if (originalStar) originalStar.classList.remove("active");
                    if (currentStarred && file.cardNode) file.cardNode.remove(); // Remove immediately if viewing Starred Filter viewport
                }
            } catch (e) { console.error("Toggle star inside details failed", e); }
        });
    }

    // Wire up download button
    const detailDownload = document.getElementById("detail-download");
    if (detailDownload) {
        const newBtn = detailDownload.cloneNode(true);
        detailDownload.parentNode.replaceChild(newBtn, detailDownload);
        newBtn.addEventListener("click", () => {
             window.location.href = `/api/files/${file.id}/download`;
        });
    }
    
    // Wire up delete button
    const detailDelete = document.getElementById("detail-delete");
    if (detailDelete) {
        const deleteBtn = detailDelete.cloneNode(true);
        detailDelete.parentNode.replaceChild(deleteBtn, detailDelete);
        deleteBtn.addEventListener("click", async () => {
             if (!confirm(`Move ${file.name} to trash?`)) return;
              try {
                  await fetch(`/api/files/${file.id}/trash`, { method: "POST" });
                  detailsOverlay.classList.remove("active");
                  if (file.cardNode) file.cardNode.remove();
                  
                  const totalStats = document.getElementById("total-stats");
                  if (totalStats) {
                       const current = parseInt(totalStats.innerText);
                       if (!isNaN(current)) {
                            totalStats.innerText = `${current - 1} Designs`;
                       }
                  }
              } catch (e) { console.error("Trash from details failed", e); }
        });
    }
    
    detailsOverlay.classList.add("active");
}

async function pollScanStatus() {
    try {
        // 1. Check Import Status FIRST
        const resImport = await fetch("/api/import/status");
        const importStatus = await resImport.json();
        const btnStopScan = document.getElementById("btn-stop-scan");
        
        if (importStatus.is_importing) {
            scanTriggerAttempts = 0; // Clear attempts
            scanProgress.classList.remove("hidden");
            if (btnScan) btnScan.classList.add("hidden");
            
            scanCount.innerText = importStatus.processed;
            scanTotal.innerText = importStatus.total;
            const percent = importStatus.total > 0 ? (importStatus.processed / importStatus.total) * 100 : 0;
            progressBarFill.style.width = `${percent}%`;
            
            scanText.innerText = importStatus.current_file 
                ? `Importing: ${importStatus.current_file.substring(0, 17)}...` 
                : "Importing from Inbox...";
                
            if (btnStopScan) {
                btnStopScan.disabled = importStatus.stop_requested;
                btnStopScan.innerText = importStatus.stop_requested ? "Stopping..." : "Stop Import";
                btnStopScan.onclick = async () => {
                    btnStopScan.disabled = true;
                    await fetch("/api/import/stop", { method: "POST" });
                };
            }
            setTimeout(pollScanStatus, 1000);
            return; // Exit, wait for import to finish
        }

        // 2. Check Scan Status IF NOT Importing
        const resScan = await fetch("/api/scan/status");
        const scanStatus = await resScan.json();
        const wasActive = !scanProgress.classList.contains("hidden");
        
        if (scanStatus.is_scanning) {
            scanTriggerAttempts = 0; // Clear attempts
            scanProgress.classList.remove("hidden");
            if (btnScan) btnScan.classList.add("hidden");
            
            scanCount.innerText = scanStatus.processed;
            scanTotal.innerText = scanStatus.total;
            const percent = scanStatus.total > 0 ? (scanStatus.processed / scanStatus.total) * 100 : 0;
            progressBarFill.style.width = `${percent}%`;
            
            scanText.innerText = scanStatus.current_file 
                ? `Scanning: ${scanStatus.current_file.substring(0, 17)}...` 
                : "Scanning Library...";
                
            if (btnStopScan) {
                btnStopScan.disabled = scanStatus.stop_requested;
                btnStopScan.innerText = scanStatus.stop_requested ? "Stopping..." : "Stop Scan";
                btnStopScan.onclick = async () => {
                    btnStopScan.disabled = true;
                    await fetch("/api/scan/stop", { method: "POST" });
                };
            }
            setTimeout(pollScanStatus, 1000);
        } else {
            if (scanTriggerAttempts > 0) {
                scanTriggerAttempts--;
                setTimeout(pollScanStatus, 1000);
                return;
            }
            scanProgress.classList.add("hidden");
            if (btnScan) {
                btnScan.classList.remove("hidden");
                btnScan.disabled = false;
                btnScan.innerHTML = '<i class="fa-solid fa-sync"></i> <span>Scan Library</span>';
            }
            if (wasActive) {
                // Refresh list if scan cycle just completed
                loadFiles(true);
                loadTags();
            }
        }
    } catch (e) {
        console.error("Failed to poll status", e);
        setTimeout(pollScanStatus, 5000);
    }
}

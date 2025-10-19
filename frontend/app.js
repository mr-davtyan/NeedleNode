let offset = 0;
const limit = 40;
let loading = false;
let hasMore = true;
let currentTag = "";
let searchTerm = "";
let currentStarred = false;

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
        try {
            await fetch("/api/scan", { method: "POST" });
            // Immediately start polling
            pollScanStatus();
            setTimeout(() => {
                btnScan.disabled = false;
                btnScan.innerHTML = '<i class="fa-solid fa-sync"></i> <span>Scan Library</span>';
            }, 2000);
        } catch (e) {
            console.error(e);
            btnScan.disabled = false;
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
        tagsList.innerHTML = tags.map(tag => 
            `<div class="tag-item" data-tag="${tag}">${tag}</div>`
        ).join("");

        // Click Tag
        document.querySelectorAll(".tag-item").forEach(el => {
            el.addEventListener("click", () => {
                document.querySelectorAll(".tag-item").forEach(t => t.classList.remove("active"));
                document.getElementById("btn-all").classList.remove("active");
                el.classList.add("active");
                currentTag = el.getAttribute("data-tag");
                loadFiles(true);
            });
        });
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
                        </div>
                    </div>
                </div>
            `;
            
            // Star Button
            const star = card.querySelector(".btn-star");
            star.addEventListener("click", async (e) => {
                e.stopPropagation(); // prevent opening details
                try {
                    const res = await fetch(`/api/files/${file.id}/star`, { method: "POST" });
                    const result = await res.json();
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
    
    // Wire up download button
    const detailDownload = document.getElementById("detail-download");
    if (detailDownload) {
        const newBtn = detailDownload.cloneNode(true);
        detailDownload.parentNode.replaceChild(newBtn, detailDownload);
        newBtn.addEventListener("click", () => {
             window.location.href = `/api/files/${file.id}/download`;
        });
    }
    
    detailsOverlay.classList.add("active");
}

async function pollScanStatus() {
    try {
        const res = await fetch("/api/scan/status");
        const status = await res.json();
        
        if (status.is_scanning) {
            scanProgress.classList.remove("hidden");
            if (btnScan) btnScan.classList.add("hidden");
            scanCount.innerText = status.processed;
            scanTotal.innerText = status.total;
            
            const percent = status.total > 0 ? (status.processed / status.total) * 100 : 0;
            progressBarFill.style.width = `${percent}%`;
            
            if (status.current_file) {
                // Shorten if file path is too long
                const fileLabel = status.current_file.length > 20 
                    ? status.current_file.substring(0, 17) + "..." 
                    : status.current_file;
                scanText.innerText = `Scanning: ${fileLabel}`;
            } else {
                scanText.innerText = "Scanning...";
            }
            
            // Update Stop Button State
            const btnStopScan = document.getElementById("btn-stop-scan");
            if (btnStopScan) {
                btnStopScan.disabled = status.stop_requested || false;
                if (status.stop_requested) {
                    btnStopScan.innerText = "Stopping...";
                } else {
                    btnStopScan.innerText = "Stop Scan 🛑";
                }
            }
            
            // Poll again in 1s
            setTimeout(pollScanStatus, 1000);
        } else {
            const wasScanning = !scanProgress.classList.contains("hidden");
            scanProgress.classList.add("hidden");
            if (btnScan) btnScan.classList.remove("hidden");
            if (wasScanning) {
                // Refresh list if scan just completed
                loadFiles(true);
                loadTags();
            }
        }
    } catch (e) {
        console.error("Failed to poll scan status", e);
        // Retry polling later
        setTimeout(pollScanStatus, 5000);
    }
}

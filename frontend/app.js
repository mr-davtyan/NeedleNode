let offset = 0;
const limit = 40;
let loading = false;
let hasMore = true;
let currentTag = "";
let searchTerm = "";

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

// Init
document.addEventListener("DOMContentLoaded", () => {
    loadTags();
    loadFiles(true); // reset
    setupInfiniteScroll();
    setupEventListeners();
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
        btnScan.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Scanning...</span>';
        try {
            await fetch("/api/scan", { method: "POST" });
            setTimeout(() => {
                loadTags();
                loadFiles(true);
                btnScan.innerHTML = '<i class="fa-solid fa-sync"></i> <span>Scan Inbox</span>';
            }, 3000); // Polling or wait
        } catch (e) {
            console.error(e);
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
        document.querySelectorAll(".tag-item").forEach(t => t.classList.remove("active"));
        document.getElementById("btn-all").classList.add("active");
        loadFiles(true);
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
                    <div class="file-meta">
                        <span>${file.stitches} Stitches</span>
                        <span>${(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                </div>
            `;
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
    
    detailsOverlay.classList.add("active");
}

// Common API address
const BASE_URL = (typeof window !== "undefined" && window.location.port === "8001") 
    ? window.location.origin 
    : "http://localhost:8001";


// Fetch categories from API and populate menus
async function loadCategories() {
    try {
        const response = await fetch(`${BASE_URL}/api/v1/categories/main`);
        if (!response.ok) return;
        
        const data = await response.json();
        const categories = Array.isArray(data) ? data : (data.data || []);
        
        // Top menu (Navbar)
        const navbar = document.querySelector("#navbar .navbar-nav");
        if (navbar) {
            navbar.innerHTML = ""; // Clear existing static items
            categories.slice(0, 5).forEach(cat => {
                navbar.innerHTML += `<li class="nav-item"><a href="#" class="nav-link category-link" data-id="${cat.id}">${cat.name}</a></li>`;
            });
            // Make the rest a dropdown
            if (categories.length > 5) {
                let dropdownHtml = `<li class="nav-item dropdown">
                    <a href="#" class="nav-link dropdown-toggle" data-bs-toggle="dropdown">Other Categories</a>
                    <ul class="dropdown-menu">`;
                categories.slice(5).forEach(cat => {
                    dropdownHtml += `<li><a href="#" class="dropdown-item category-link" data-id="${cat.id}">${cat.name}</a></li>`;
                });
                dropdownHtml += `</ul></li>`;
                navbar.innerHTML += dropdownHtml;
            }
        }
        

                
        // Add click event to category links
        document.querySelectorAll('.category-link').forEach(link => {
            link.addEventListener('click', async function(e) {
                e.preventDefault();
                
                const catId = this.getAttribute('data-id');
                const catName = this.innerText;
                await loadProductsByCategory(catId, catName);
            });
        });
        
    } catch (error) {
        console.error("Failed to load categories:", error);
    }
}

// Fetch Products by Selected Category
async function loadProductsByCategory(categoryId, categoryName) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = `
        <div class="col-12 text-center mt-5">
            <div class="spinner-border text-primary" role="status"></div>
            <h5 class="mt-3 text-muted">Loading products in ${categoryName}...</h5>
        </div>
    `;
    
    try {
        const response = await fetch(`${BASE_URL}/api/v1/products/main-category/${categoryId}`);
        if (!response.ok) throw new Error("Network error");
        
        const data = await response.json();
        const productsList = Array.isArray(data) ? data : (data.data || []);
        
        // Update title
        const sectionTitle = document.querySelector("#sectionTitle");
        if (sectionTitle) sectionTitle.innerText = `${categoryName} (${productsList.length} Products)`;
        
        renderProducts(productsList);
    } catch (error) {
        console.error("Failed to load category products:", error);
        resultsDiv.innerHTML = `<div class="col-12 text-center mt-5 text-danger"><h5>An error occurred while fetching products.</h5></div>`;
    }
}

// Initial Load for Homepage - Demo Products
async function loadProducts() {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = `
        <div class="col-12 text-center mt-5">
            <div class="spinner-border text-primary" role="status"></div>
            <h5 class="mt-3 text-muted">Ürünler Yükleniyor...</h5>
        </div>
    `;
    
    await loadCategories();

    try {
        const response = await fetch(`${BASE_URL}/api/v1/products?limit=12`);
        if (!response.ok) throw new Error("Network error");
        
        const data = await response.json();
        const productsList = Array.isArray(data) ? data : (data.data || []);
        
        const sectionTitle = document.querySelector("#sectionTitle");
        if (sectionTitle) sectionTitle.innerText = `Öne Çıkan Ürünler`;
        
        renderProducts(productsList);
    } catch (error) {
        console.error("Failed to load initial products:", error);
        resultsDiv.innerHTML = `<div class="col-12 text-center mt-5 text-danger"><h5>Ürünler yüklenirken bir hata oluştu.</h5></div>`;
    }
}

// Common Function to Render Product Cards
function renderProducts(products, isAiSearch = false) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = ""; // Clear content

    if (!products || products.length === 0) {
        resultsDiv.innerHTML = `<div class="col-12 text-center mt-5"><h5>No products found matching your criteria.</h5></div>`;
        return;
    }

    products.forEach(p => {
        const priceText = p.price ? `${p.price} ${p.currency || 'TL'}` : 'Fiyat Belirtilmemiş';
        const imageUrl = p.image_url || p.images?.[0] || "https://via.placeholder.com/300x300?text=No+Image";
        const productLink = `product.html?id=${p.id}`;
        const productName = p.name || p.title || 'Ürün Adı Yok';

        // Rating calculation
        const rating = p.rating || 0;
        const reviewCount = p.review_count || p.rating_count || 0;
        let starsHtml = '';
        if (rating > 0) {
            const fullStars = Math.floor(rating);
            const halfStar = (rating % 1) >= 0.5 ? 1 : 0;
            const emptyStars = 5 - fullStars - halfStar;
            
            for(let i=0; i<fullStars; i++) starsHtml += '<i class="fa-solid fa-star text-warning" style="font-size:0.8rem;"></i>';
            if(halfStar) starsHtml += '<i class="fa-solid fa-star-half-stroke text-warning" style="font-size:0.8rem;"></i>';
            for(let i=0; i<emptyStars; i++) starsHtml += '<i class="fa-regular fa-star text-warning" style="font-size:0.8rem;"></i>';
        } else {
            starsHtml = '<span class="text-muted small">Değerlendirme yok</span>';
        }
        
        const ratingText = rating > 0 ? `<span class="fw-bold ms-1" style="font-size:0.85rem;">${rating.toFixed(1)}</span> <span class="text-muted ms-1" style="font-size:0.75rem;">(${reviewCount} değerlendirme)</span>` : '';

        let badgeHtml = "";
        // Show AI match badge if isAiSearch is true or score < 100
        if (isAiSearch && p.cross_encoder_score) {
            badgeHtml = `<span class="badge bg-success position-absolute top-0 end-0 m-2 shadow-sm">Eşleşme: ${p.cross_encoder_score.toFixed(1)}%</span>`;
        } else if (p.cross_encoder_score && p.cross_encoder_score < 100) {
            badgeHtml = `<span class="badge bg-success position-absolute top-0 end-0 m-2 shadow-sm">Eşleşme: ${p.cross_encoder_score.toFixed(1)}%</span>`;
        }

        // Sol kenarda küçücük benzerlik oranı badge'i
        let similarityBadgeHtml = "";
        if (p.similarity !== undefined && p.similarity !== null) {
            const simScore = Math.max(0, Math.min(100, (p.similarity * 100)));
            const formattedSim = simScore.toFixed(1);
            similarityBadgeHtml = `
                <span class="badge bg-dark bg-opacity-75 text-white position-absolute top-0 start-0 m-2 shadow-sm border border-secondary" 
                      style="font-size: 0.68rem; font-weight: 600; padding: 2px 5px; z-index: 5; backdrop-filter: blur(4px); border-radius: 4px;"
                      title="Vektör Benzerlik Skoru: %${formattedSim}">
                    <i class="fa-solid fa-bullseye text-warning me-1" style="font-size: 0.6rem;"></i>%${formattedSim}
                </span>`;
        }

        const brandText = p.brand ? `<span class="fw-bold text-dark me-1" style="font-size: 0.9rem;">${p.brand}</span>` : '';

        resultsDiv.innerHTML += `
            <div class="col">
                <div class="card h-100 border product-card" style="border-radius: 8px; overflow: hidden; transition: box-shadow 0.2s; box-shadow: 0 1px 4px rgba(0,0,0,0.05);" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'" onmouseout="this.style.boxShadow='0 1px 4px rgba(0,0,0,0.05)'">
                    <div class="img-wrap bg-white" style="height: 250px; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative;">
                        <a href="${productLink}" class="d-flex align-items-center justify-content-center w-100 h-100 text-decoration-none">
                            <img src="${imageUrl}" alt="${productName}" style="max-height: 100%; max-width: 100%; object-fit: cover;">
                        </a>
                        ${similarityBadgeHtml}
                        ${badgeHtml}
                        
                        <!-- AI Add Button (Shows on Hover / Selected) -->
                        <div class="position-absolute p-2 ai-hover-overlay" style="top: 0; right: 0; z-index: 10;">
                            <button class="btn btn-sm btn-warning rounded shadow fw-bold ai-add-btn" 
                                    title="AI Bağlamına Ekle / Çıkar" 
                                    data-id="${p.id}" 
                                    data-name="${(p.name || p.title || '').replace(/"/g, '&quot;')}" 
                                    data-image="${imageUrl}" 
                                    data-price="${priceText}"
                                    onclick="event.stopPropagation(); toggleAIContext(this.getAttribute('data-id'), this.getAttribute('data-name'), this.getAttribute('data-image'), this.getAttribute('data-price'))">
                                <i class="fa-solid fa-plus me-1"></i> Ekle
                            </button>
                        </div>
                    </div>

                    <div class="info-wrap p-2 d-flex flex-column bg-white text-start" style="flex-grow: 1;">
                        <a href="${productLink}" class="text-decoration-none" style="color: inherit;">
                            <div class="title text-truncate-2 d-block mb-1" title="${productName}" style="color: #333; font-size: 0.85rem; line-height: 1.3; height: 2.6em; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                                ${brandText}${productName}
                            </div>
                        </a>
                        
                        <div class="mb-2 mt-1 d-flex align-items-center">
                            ${starsHtml}
                            ${ratingText}
                        </div>
                        
                        <div class="mt-auto pt-1 text-start">
                            <a href="${productLink}" class="text-decoration-none">
                                <span class="price-discount text-danger fw-bold" style="font-size: 1.1rem;">${priceText}</span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
}

// Global context array and session ID
window.aiSelectedProducts = [];
window.aiSessionId = "web-" + Math.random().toString(36).slice(2, 10);

function toggleAIContext(id, name, image, price) {
    const numId = Number(id) || id;
    const exists = window.aiSelectedProducts.find(p => String(p.id) === String(numId));
    if (exists) {
        window.aiSelectedProducts = window.aiSelectedProducts.filter(p => String(p.id) !== String(numId));
    } else {
        window.aiSelectedProducts.push({ id: numId, name, image, price });
    }
    renderAIContext();
}
window.toggleAIContext = toggleAIContext;
window.addToAIContext = toggleAIContext;

function removeFromAIContext(id) {
    window.aiSelectedProducts = window.aiSelectedProducts.filter(p => String(p.id) !== String(id));
    renderAIContext();
}

function clearAIContext() {
    window.aiSelectedProducts = [];
    renderAIContext();
}
window.clearAIContext = clearAIContext;

function syncCardButtons() {
    const selectedIds = new Set(window.aiSelectedProducts.map(p => String(p.id)));
    document.querySelectorAll(".ai-add-btn").forEach(btn => {
        const pid = String(btn.getAttribute("data-id"));
        if (selectedIds.has(pid)) {
            btn.classList.remove("btn-warning");
            btn.classList.add("btn-success");
            btn.innerHTML = '<i class="fa-solid fa-check me-1"></i> Seçildi';
        } else {
            btn.classList.remove("btn-success");
            btn.classList.add("btn-warning");
            btn.innerHTML = '<i class="fa-solid fa-plus me-1"></i> Ekle';
        }
    });
}

function renderAIContext() {
    const contextArea = document.getElementById("aiContextArea");
    const badge = document.getElementById("aiSelectedBadge");
    const quickActions = document.getElementById("aiQuickActions");

    syncCardButtons();

    if (badge) {
        if (window.aiSelectedProducts.length > 0) {
            badge.textContent = window.aiSelectedProducts.length;
            badge.classList.remove("d-none");
        } else {
            badge.classList.add("d-none");
        }
    }

    if (!contextArea) return;

    if (window.aiSelectedProducts.length === 0) {
        contextArea.style.setProperty("display", "none", "important");
        contextArea.innerHTML = "";
        if (quickActions) {
            quickActions.classList.add("d-none");
            quickActions.classList.remove("d-flex");
            quickActions.innerHTML = "";
        }
        return;
    }

    contextArea.style.setProperty("display", "flex", "important");
    contextArea.innerHTML = window.aiSelectedProducts.map(p => `
        <div class="d-inline-flex align-items-center bg-white border rounded shadow-sm p-1 position-relative" style="min-width: 150px; max-width: 200px;">
            <img src="${p.image}" class="rounded" style="width: 30px; height: 30px; object-fit: cover; margin-right: 8px;">
            <div class="text-truncate" style="font-size: 0.75rem; line-height: 1.1; padding-right: 14px;">
                <div class="fw-bold text-truncate">${p.name}</div>
                <div class="text-primary">${p.price}</div>
            </div>
            <button onclick="removeFromAIContext('${p.id}')" class="btn btn-sm btn-link text-danger position-absolute top-0 end-0 p-0 m-1" style="line-height: 0.5;">
                <i class="fa-solid fa-times-circle"></i>
            </button>
        </div>
    `).join("") + `
        <button onclick="clearAIContext()" class="btn btn-sm btn-outline-secondary align-self-center ms-1" style="font-size: 0.7rem; white-space: nowrap;">
            Temizle
        </button>
    `;

    if (quickActions) {
        quickActions.classList.remove("d-none");
        quickActions.classList.add("d-flex");
        const chips = window.aiSelectedProducts.length >= 2
            ? [
                { label: "⚖️ Karşılaştır", query: "Seçtiğim ürünleri detaylıca karşılaştır." },
                { label: "🏆 Hangisi daha iyi?", query: "Seçtiğim ürünlerden hangisini almak daha mantıklı, neden?" },
              ]
            : [
                { label: "💬 Yorumları Özetle", query: "Seçtiğim ürünün müşteri yorumlarını artıları ve eksileriyle özetle." },
                { label: "📋 Detayları Göster", query: "Seçtiğim ürünün tüm teknik özelliklerini ve detaylarını anlat." },
              ];
        quickActions.innerHTML = chips.map(c => `
            <button type="button" class="btn btn-sm btn-outline-primary rounded-pill py-0 px-2" style="font-size: 0.75rem;" onclick="sendMessageToAI('${c.query.replace(/'/g, "\\'")}')">
                ${c.label}
            </button>
        `).join("");
    }
}

// Helper to open the AI offcanvas
function openAIPanel() {
    const aiPanelEl = document.getElementById('aiPanel');
    if (aiPanelEl) {
        const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(aiPanelEl);
        bsOffcanvas.show();
    }
}

function formatMarkdown(text) {
    return (text || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/^### (.*)$/gm, '<div class="fw-bold text-primary mt-2 mb-1">$1</div>')
        .replace(/^## (.*)$/gm, '<div class="fw-bold fs-6 text-dark mt-2 mb-1">$1</div>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^- (.*)$/gm, '<div class="ms-2">• $1</div>')
        .replace(/\n/g, '<br>');
}

// AI Chat Interaction Logic
async function sendMessageToAI(overrideQuery) {
    const inputEl = document.getElementById("chatInput");
    const query = (typeof overrideQuery === "string" ? overrideQuery : inputEl.value).trim();
    if (!query) return;

    const chatMessages = document.getElementById("chatMessages");

    // Add user message to UI
    chatMessages.innerHTML += `
        <div class="d-flex mb-3 justify-content-end">
            <div class="bg-primary text-white p-2 rounded shadow-sm" style="max-width: 80%; border-radius: 15px 15px 0 15px !important;">
                ${query}
            </div>
        </div>
    `;
    if (typeof overrideQuery !== "string") inputEl.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add typing indicator
    const typingId = "typing-" + Date.now();
    chatMessages.innerHTML += `
        <div id="${typingId}" class="d-flex mb-3">
            <div class="bg-light text-dark p-2 rounded shadow-sm border" style="max-width: 80%; border-radius: 15px 15px 15px 0 !important;">
                <i class="fa-solid fa-ellipsis fa-fade"></i> Düşünüyor...
            </div>
        </div>
    `;
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch("http://localhost:8000/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: query,
                session_id: window.aiSessionId,
                context_products: window.aiSelectedProducts
            })
        });

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        const data = await response.json();
        
        // Remove typing indicator
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        const formattedResponse = formatMarkdown(data.response);

        // Add AI response to UI
        let miniCardsHtml = "";
        if (Array.isArray(data.found_products) && data.found_products.length > 0) {
            const topTwo = data.found_products.slice(0, 2);
            miniCardsHtml = `
                <div class="mt-2 pt-2 border-top d-flex flex-column gap-2">
                    ${topTwo.map(p => {
                        const img = p.image_url || p.images?.[0] || "https://via.placeholder.com/60x60?text=Ürün";
                        const price = p.price ? `${p.price} ${p.currency || 'TRY'}` : 'Fiyat Yok';
                        return `
                            <a href="product.html?id=${p.id}" class="d-flex align-items-center gap-2 p-2 bg-light rounded border text-decoration-none text-dark">
                                <img src="${img}" class="rounded" style="width: 44px; height: 44px; object-fit: cover;">
                                <div class="overflow-hidden flex-grow-1">
                                    <div class="fw-bold text-truncate" style="font-size: 0.78rem;">${p.name || 'Ürün'}</div>
                                    <div class="text-danger fw-bold" style="font-size: 0.78rem;">${price}</div>
                                </div>
                                <i class="fa-solid fa-chevron-right text-muted small"></i>
                            </a>
                        `;
                    }).join("")}
                </div>
            `;
        }

        chatMessages.innerHTML += `
            <div class="d-flex mb-3">
                <div class="bg-white text-dark p-3 rounded shadow-sm border" style="max-width: 90%; border-radius: 15px 15px 15px 0 !important;">
                    ${formattedResponse}
                    ${miniCardsHtml}
                </div>
            </div>
        `;
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // AI arama yaptıysa en benzer 20 ürünü ana ekranda listele
        if (Array.isArray(data.found_products) && data.found_products.length > 0) {
            const sectionTitle = document.querySelector("#sectionTitle");
            if (sectionTitle) {
                sectionTitle.innerHTML = `<i class="fa-solid fa-sparkles text-warning me-2"></i>AI Asistanın Bulduğu Ürünler <span class="badge bg-secondary fs-6 ms-2">${data.found_products.length} Ürün</span>`;
            }
            renderProducts(data.found_products, true);
            syncCardButtons();
        }
        
        // Clear context after successful query if desired (optional)
        // window.aiSelectedProducts = [];
        // renderAIContext();

    } catch (error) {
        console.error("AI Error:", error);
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();
        
        chatMessages.innerHTML += `
            <div class="d-flex mb-3">
                <div class="bg-danger text-white p-2 rounded shadow-sm" style="max-width: 80%; border-radius: 15px 15px 15px 0 !important;">
                    Üzgünüm, şu an bağlantı kuramıyorum. Lütfen sistemin çalıştığından emin olun.
                </div>
            </div>
        `;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Arama Çubuğu ve Vektör Benzerliği Arama Mantığı
async function search(customQuery) {
    const searchInput = document.getElementById("searchInput");
    const query = (customQuery !== undefined ? customQuery : (searchInput ? searchInput.value : "")).trim();
    if (!query) return;

    if (searchInput) {
        searchInput.value = query;
    }

    const resultsDiv = document.getElementById("results");
    const sectionTitle = document.querySelector("#sectionTitle");

    // Yükleniyor durumu göster
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="col-12 text-center my-5 py-5">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;"></div>
                <h5 class="mt-3 text-muted">"${query}" için en yakın ürünler aranıyor...</h5>
                <p class="text-secondary small"><i class="fa-solid fa-brain me-1 text-primary"></i>Vektör benzerliği hesaplanıyor</p>
            </div>
        `;
    }

    if (sectionTitle) {
        sectionTitle.innerHTML = `<i class="fa-solid fa-magnifying-glass text-primary me-2"></i>"${query}" aranıyor...`;
    }

    try {
        const response = await fetch(`${BASE_URL}/api/v1/products/closest`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: query,
                limit: 50
            })
        });

        if (!response.ok) {
            throw new Error(`API Hatası: ${response.status}`);
        }

        const data = await response.json();
        let products = Array.isArray(data) ? data : (data.data || []);

        // Benzerlik oranlarına göre azalan sırada sırala
        products.sort((a, b) => (b.similarity || 0) - (a.similarity || 0));

        if (sectionTitle) {
            sectionTitle.innerHTML = `<i class="fa-solid fa-magnifying-glass text-primary me-2"></i>"${query}" İçin En Yakın Ürünler <span class="badge bg-secondary fs-6 ms-2">${products.length} Ürün</span>`;
        }

        renderProducts(products);

        // Sonuç alanına yumuşak geçiş yap
        if (resultsDiv) {
            resultsDiv.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    } catch (error) {
        console.error("Vektör arama hatası:", error);
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="col-12 text-center my-5 py-5 text-danger">
                    <i class="fa-solid fa-circle-exclamation fa-2x mb-3"></i>
                    <h5>Ürünler aranırken bir hata oluştu.</h5>
                    <p class="text-muted small">${error.message}</p>
                </div>
            `;
        }
    }
}
window.search = search;

document.addEventListener("DOMContentLoaded", () => {
    // Bind search input Enter key
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                search();
            }
        });
    }

    // URL'de ?search=... parametresi varsa otomatik ara
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get("search");
    if (searchQuery) {
        if (searchInput) searchInput.value = searchQuery;
        search(searchQuery);
    } else {
        loadProducts();
    }
    
    // Bind chat events
    const sendBtn = document.getElementById("chatSendBtn");
    const inputEl = document.getElementById("chatInput");
    
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessageToAI);
    }
    if (inputEl) {
        inputEl.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                sendMessageToAI();
            }
        });
    }
});
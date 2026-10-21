// ==========================================
// Arama Çubuğu ve Vektör Benzerliği Arama Mantığı
// ==========================================

async function search(customQuery) {
    const searchInput = document.getElementById("searchInput");
    const query = (customQuery !== undefined ? customQuery : (searchInput ? searchInput.value : "")).trim();
    if (!query) return;

    if (searchInput) {
        searchInput.value = query;
    }

    // Eğer product.html gibi index dışı bir sayfadaysak index.html'e yönlendir
    const isIndexPage = !!document.getElementById("results");
    if (!isIndexPage) {
        window.location.href = `index.html?search=${encodeURIComponent(query)}`;
        return;
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
        const apiUrl = typeof BASE_URL !== "undefined" ? BASE_URL : "http://localhost:8001";
        const response = await fetch(`${apiUrl}/api/v1/products/closest`, {
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

        // Benzerlik oranlarına göre azalan sırada sırala (yüksek benzerlik en başta)
        products.sort((a, b) => (b.similarity || 0) - (a.similarity || 0));

        if (sectionTitle) {
            sectionTitle.innerHTML = `<i class="fa-solid fa-magnifying-glass text-primary me-2"></i>"${query}" İçin En Yakın Ürünler <span class="badge bg-secondary fs-6 ms-2">${products.length} Ürün</span>`;
        }

        renderProducts(products);

        // Sonuç alanına yumuşak geçiş yap
        resultsDiv.scrollIntoView({ behavior: "smooth", block: "start" });
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

// Global erişim
window.search = search;

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");

    // Enter tuşuna basıldığında aramayı başlat
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
        if (searchInput) {
            searchInput.value = searchQuery;
        }
        search(searchQuery);
    }
});
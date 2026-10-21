const BASE_URL = (typeof window !== "undefined" && window.location.port === "8001") 
    ? window.location.origin 
    : "http://localhost:8001";

document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');

    if (!productId) {
        const titleEl = document.getElementById("productTitle");
        if (titleEl) titleEl.innerText = "Ürün Bulunamadı (Geçersiz ID).";
        return;
    }

    try {
        // 1. Fetch product details
        const response = await fetch(`${BASE_URL}/api/v1/products/${productId}`);
        if (!response.ok) {
            throw new Error(`Ürün yüklenemedi (HTTP ${response.status})`);
        }

        const data = await response.json();
        const product = data.data || data;

        // Populate basic text
        const titleEl = document.getElementById("productTitle");
        if (titleEl) titleEl.innerText = product.name || product.title || "İsimsiz Ürün";

        const breadcrumbTitleEl = document.getElementById("breadcrumbTitle");
        if (breadcrumbTitleEl) breadcrumbTitleEl.innerText = product.name || product.title || "Ürün";
        
        const breadcrumbCatEl = document.getElementById("breadcrumbCategory");
        if (breadcrumbCatEl) breadcrumbCatEl.innerText = product.full_path || product.brand || "Kategori";
        
        const priceText = product.price ? `${product.price} ${product.currency || 'TL'}` : 'Fiyat Belirtilmemiş';
        const priceEl = document.getElementById("productPrice");
        if (priceEl) priceEl.innerText = priceText;

        // Rating Stars
        const ratingStars = document.getElementById("ratingStars");
        const rating = Number(product.rating) || 0;
        const reviewCount = product.review_count || product.rating_count || 0;
        
        if (ratingStars) {
            ratingStars.innerHTML = "";
            const fullStars = Math.floor(rating);
            const halfStar = (rating % 1) >= 0.5 ? 1 : 0;
            const emptyStars = Math.max(0, 5 - fullStars - halfStar);
            
            for (let i = 0; i < fullStars; i++) ratingStars.innerHTML += '<i class="fa-solid fa-star text-warning"></i>';
            if (halfStar) ratingStars.innerHTML += '<i class="fa-solid fa-star-half-stroke text-warning"></i>';
            for (let i = 0; i < emptyStars; i++) ratingStars.innerHTML += '<i class="fa-regular fa-star text-warning"></i>';
            
            const ratingScoreEl = document.getElementById("ratingScoreText");
            if (ratingScoreEl) ratingScoreEl.innerText = rating > 0 ? rating.toFixed(1) : "";
            
            const ratingCountEl = document.getElementById("ratingCount");
            if (ratingCountEl) ratingCountEl.innerText = `${reviewCount} Değerlendirme`;
        }

        // Images Carousel
        const carouselInner = document.getElementById("carouselInner");
        if (carouselInner) {
            carouselInner.innerHTML = "";
            let images = [];
            
            if (typeof product.images === "string") {
                try { images = JSON.parse(product.images); } catch(e) { images = [product.images]; }
            } else if (Array.isArray(product.images)) {
                images = product.images;
            } else if (product.image_url) {
                images = [product.image_url];
            }

            if (!Array.isArray(images) || images.length === 0) {
                images = ["https://via.placeholder.com/600x600?text=Görsel+Yok"];
            }

            images.forEach((imgUrl, index) => {
                carouselInner.innerHTML += `
                    <div class="carousel-item ${index === 0 ? 'active' : ''} h-100">
                        <div class="d-flex align-items-center justify-content-center h-100 p-2">
                            <img src="${imgUrl}" alt="Ürün Görseli ${index + 1}" style="max-width:100%; max-height:100%; object-fit:contain;">
                        </div>
                    </div>
                `;
            });
            
            // Hide carousel controls if only 1 image
            if (images.length <= 1) {
                document.querySelectorAll('.carousel-control-prev, .carousel-control-next').forEach(el => el.style.display = 'none');
            }
        }

        // Attributes Table
        const attributesTable = document.querySelector("#attributesTable tbody");
        if (attributesTable) {
            attributesTable.innerHTML = "";
            let attrs = product.attributes;
            if (typeof attrs === "string") {
                try { attrs = JSON.parse(attrs); } catch(e) { attrs = {}; }
            }
            if (attrs && typeof attrs === 'object') {
                for (const [key, value] of Object.entries(attrs)) {
                    if (value && typeof value !== 'object') {
                        attributesTable.innerHTML += `
                            <tr>
                                <th class="w-50 text-muted bg-light">${key}</th>
                                <td class="w-50 fw-medium">${value}</td>
                            </tr>
                        `;
                    }
                }
            }
            if (product.brand) {
                attributesTable.innerHTML = `<tr><th class="w-50 text-muted bg-light">Marka</th><td class="w-50 fw-medium">${product.brand}</td></tr>` + attributesTable.innerHTML;
            }
            
            if (attributesTable.innerHTML === "") {
                attributesTable.innerHTML = `<tr><td colspan="2" class="text-muted">Bu ürüne ait özellik bilgisi bulunamadı.</td></tr>`;
            }
        }

        // Fetch Reviews (non-blocking)
        try {
            await loadReviews(productId);
        } catch (revError) {
            console.warn("Reviews could not be loaded:", revError);
        }

    } catch (error) {
        console.error("Error loading product:", error);
        const titleEl = document.getElementById("productTitle");
        if (titleEl) titleEl.innerText = "Ürün yüklenirken bir hata oluştu: " + error.message;
    }
});

async function loadReviews(productId) {
    const reviewsContainer = document.getElementById("reviewsContainer");
    if (!reviewsContainer) return;
    
    try {
        const response = await fetch(`${BASE_URL}/api/v1/reviews/product/${productId}`);
        if (!response.ok) throw new Error("Yorumlar yüklenemedi.");
        
        const reviews = await response.json();
        
        if (!reviews || reviews.length === 0) {
            reviewsContainer.innerHTML = `<div class="text-muted text-center py-4">Bu ürün için henüz değerlendirme yapılmamış. İlk değerlendiren siz olun!</div>`;
            return;
        }

        reviewsContainer.innerHTML = ""; // clear loading
        
        // Render first 20 reviews
        reviews.slice(0, 20).forEach(review => {
            const stars = review.rating || 5;
            let starsHtml = "";
            for (let i = 0; i < 5; i++) {
                if (i < stars) starsHtml += '<i class="fa-solid fa-star text-warning" style="font-size: 0.85rem;"></i>';
                else starsHtml += '<i class="fa-regular fa-star text-warning" style="font-size: 0.85rem;"></i>';
            }
            
            const author = review.author || "Gizli Kullanıcı";
            const authorParts = author.split(" ");
            const maskedAuthor = authorParts.map(p => p.charAt(0) + "***").join(" ");
            
            const dateObj = new Date(review.review_date);
            const dateStr = !isNaN(dateObj) ? dateObj.toLocaleDateString('tr-TR') : review.review_date;
            
            reviewsContainer.innerHTML += `
                <div class="review-item border-bottom py-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            ${starsHtml}
                        </div>
                        <div class="text-muted small">
                            ${dateStr}
                        </div>
                    </div>
                    <p class="mb-2 text-dark" style="font-size: 0.95rem; line-height: 1.5;">${review.review_text || ""}</p>
                    <div class="d-flex align-items-center text-muted small">
                        <span class="fw-bold me-2">${maskedAuthor}</span>
                        <span class="text-success"><i class="fa-solid fa-check-circle me-1"></i> Ürünü Satın Aldı</span>
                    </div>
                </div>
            `;
        });
        
    } catch (error) {
        console.error("Error loading reviews:", error);
        reviewsContainer.innerHTML = `<div class="text-danger text-center py-4">Değerlendirmeler yüklenirken bir hata oluştu.</div>`;
    }
}

// Arama kutusu product sayfasından çağrılırsa index'e yönlendir
function search() {
    const searchInput = document.getElementById("searchInput");
    const query = searchInput ? searchInput.value.trim() : "";
    if (query) {
        window.location.href = `index.html?search=${encodeURIComponent(query)}`;
    }
}
window.search = search;
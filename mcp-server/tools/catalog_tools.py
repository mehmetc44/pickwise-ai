from typing import Any
import httpx

from config import settings


def _format_product_for_llm(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "brand": data.get("brand"),
        "category": data.get("full_path"),
        "price": data.get("price"),
        "currency": data.get("currency", "TRY"),
        "gender": data.get("gender"),
        "color": data.get("color"),
        "rating": data.get("rating"),
        "rating_count": data.get("rating_count"),
        "review_count": data.get("review_count"),
        "attributes": data.get("attributes"),
    }


def get_closest_products(query: str, limit: int = 8) -> list[dict[str, Any]]:
    """
    Kullanıcının arama sorgusuna anlamsal (vektör benzerliği) olarak en yakın ürünleri katalogdan getirir.
    """
    url = f"{settings.CATALOG_API_URL}/api/v1/products/closest"
    payload = {"query": query, "limit": limit}
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            products = resp.json()

        return [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "brand": p.get("brand"),
                "category": p.get("full_path"),
                "price": p.get("price"),
                "currency": p.get("currency", "TRY"),
                "rating": p.get("rating"),
                "review_count": p.get("review_count"),
                "similarity": p.get("similarity"),
            }
            for p in products
        ]
    except Exception as exc:
        return [{"error": f"Ürünler getirilemedi: {exc}"}]


def get_product_details(product_id: int) -> dict[str, Any]:
    """
    Tek bir ürünün teknik özelliklerini (attributes), fiyatını, puanını ve kategorisini ID üzerinden getirir.
    """
    url = f"{settings.CATALOG_API_URL}/api/v1/products/{product_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            if resp.status_code == 404:
                return {"error": f"ID={product_id} olan ürün bulunamadı."}
            resp.raise_for_status()
            return _format_product_for_llm(resp.json())
    except Exception as exc:
        return {"error": f"Ürün detayı getirilemedi: {exc}"}


def compare_products(product_ids: list[int]) -> list[dict[str, Any]]:
    """
    Birden fazla ürünün detaylarını (fiyat, marka, puan, kategori ve teknik özellikler) karşılaştırma için topluca getirir.
    """
    results: list[dict[str, Any]] = []
    with httpx.Client(timeout=10.0) as client:
        for pid in product_ids:
            url = f"{settings.CATALOG_API_URL}/api/v1/products/{pid}"
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    results.append(_format_product_for_llm(resp.json()))
                else:
                    results.append({"id": pid, "error": f"Bulunamadı (HTTP {resp.status_code})"})
            except Exception as exc:
                results.append({"id": pid, "error": str(exc)})
    return results


def get_product_reviews(product_id: int, limit: int = 20) -> list[dict[str, Any]]:
    """
    Belirli bir ürüne ait müşteri yorumlarını ve puanlarını getirir.
    """
    url = f"{settings.CATALOG_API_URL}/api/v1/reviews/product/{product_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            reviews = resp.json()
            return reviews[:limit] if isinstance(reviews, list) else []
    except Exception as exc:
        return [{"error": f"Yorumlar getirilemedi: {exc}"}]

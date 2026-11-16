import os
from typing import Any
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

CATALOG_API_URL = os.getenv("CATALOG_API_URL", "http://localhost:8001").rstrip("/")

mcp = FastMCP("AgenticCommerceMCP")


@mcp.tool()
def get_closest_products(query: str, limit: int = 8) -> list[dict[str, Any]]:
    """
    Kullanıcının arama sorgusuna anlamsal (vektör benzerliği) olarak en yakın ürünleri katalogdan getirir.
    """
    url = f"{CATALOG_API_URL}/api/v1/products/closest"
    payload = {"query": query, "limit": limit}
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        return [{"error": f"Ürünler getirilemedi: {exc}"}]


@mcp.tool()
def get_product_details(product_id: int) -> dict[str, Any]:
    """
    Tek bir ürünün tüm teknik özelliklerini, fiyatını, puanını ve kategorisini ID üzerinden getirir.
    """
    url = f"{CATALOG_API_URL}/api/v1/products/{product_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            if resp.status_code == 404:
                return {"error": f"ID={product_id} olan ürün bulunamadı."}
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        return {"error": f"Ürün detayı getirilemedi: {exc}"}


@mcp.tool()
def compare_products(product_ids: list[int]) -> list[dict[str, Any]]:
    """
    Birden fazla ürünün detaylarını (fiyat, marka, puan, kategori ve teknik özellikler) karşılaştırma için topluca getirir.
    """
    results: list[dict[str, Any]] = []
    with httpx.Client(timeout=10.0) as client:
        for pid in product_ids:
            url = f"{CATALOG_API_URL}/api/v1/products/{pid}"
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    results.append({
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "brand": data.get("brand"),
                        "price": data.get("price"),
                        "currency": data.get("currency"),
                        "rating": data.get("rating"),
                        "rating_count": data.get("rating_count"),
                        "review_count": data.get("review_count"),
                        "category": data.get("full_path"),
                        "attributes": data.get("attributes"),
                        "product_url": data.get("product_url"),
                    })
                else:
                    results.append({"id": pid, "error": f"Bulunamadı (HTTP {resp.status_code})"})
            except Exception as exc:
                results.append({"id": pid, "error": str(exc)})
    return results


@mcp.tool()
def get_product_reviews(product_id: int, limit: int = 20) -> list[dict[str, Any]]:
    """
    Belirli bir ürüne ait müşteri yorumlarını ve puanlarını getirir.
    """
    url = f"{CATALOG_API_URL}/api/v1/reviews/product/{product_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            reviews = resp.json()
            return reviews[:limit] if isinstance(reviews, list) else []
    except Exception as exc:
        return [{"error": f"Yorumlar getirilemedi: {exc}"}]


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)


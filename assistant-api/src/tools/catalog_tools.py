import requests
from langchain_core.tools import tool
from rag.embedder import embedder
from core.config import settings

@tool
def get_closest_categories(query: str, limit: int = 5) -> list[dict]:
    """Kullanıcının aramasına en uygun kategorileri veritabanından bulur.
    LLM bu aracı kullanarak arama cümlesini verir. Bu araç cümleyi vektöre çevirip veritabanında arar.
    """
    try:
        # catalog-api /api/v1/categories/closest endpoint'ine doğrudan metin sorgusunu gönder
        url = f"{settings.CATALOG_API_URL}/api/v1/categories/closest"
        payload = {
            "query": query,
            "limit": limit
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return [{"error": f"Kategoriler getirilemedi. Status: {response.status_code}"}]
            
    except Exception as e:
        return [{"error": f"Bir hata oluştu: {str(e)}"}]

@tool
def list_closest_products(query: str, category_id: int = None, limit: int = 5) -> list[dict]:
    """Kullanıcının aramasına en uygun ürünleri veritabanından bulur.
    İsteğe bağlı olarak category_id ile belirli bir kategori filtrelenebilir.
    """
    try:
        url = f"{settings.CATALOG_API_URL}/api/v1/products/closest"
        payload = {
            "query": query,
            "category_id": category_id,
            "limit": limit
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return [{"error": f"Ürünler getirilemedi. Status: {response.status_code}"}]
    except Exception as e:
        return [{"error": f"Bir hata oluştu: {str(e)}"}]

@tool
def get_category_filters(category_id: int) -> dict:
    """Kategoriye ait dinamik filtreleri (renk, beden, marka vb.) getirir."""
    # TODO: MCP veya catalog-api üzerinden doldurulacak
    raise NotImplementedError("Henüz implement edilmedi")

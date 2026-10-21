from typing import Union, List, Optional
from repositories.product_repository import ProductRepository
from repositories.category_repository import CategoryRepository
from services.embedding_service import EmbeddingService

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()
        self.category_repository = CategoryRepository()
        self.embedder = EmbeddingService()

    def get_products(self, limit: int = 100):
        return self.repository.get_all(limit=limit)

    def get_product(self, product_id: int):
        return self.repository.get_by_id(product_id)

    def get_products_by_category(self, category_id: int, limit: int = 100):
        return self.repository.get_by_category_id(category_id, limit)

    def get_products_by_main_category(self, category_id: int, limit: int = 100):
        category = self.category_repository.get_by_id(category_id)
        if not category:
            return []
        
        main_category_path = category.get("full_path")
        return self.repository.get_by_main_category(main_category_path, limit)

    def get_closest_products(self, query: Union[str, List[float]], limit: int = 10, category_id: Optional[int] = None):
        if isinstance(query, str):
            vector = self.embedder.embed_text(query)
        else:
            vector = query
        return self.repository.get_closest(vector, limit=limit, category_id=category_id)


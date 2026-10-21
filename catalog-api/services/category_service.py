from typing import Union, List
from repositories.category_repository import CategoryRepository
from services.embedding_service import EmbeddingService

class CategoryService:
    def __init__(self):
        self.repository = CategoryRepository()
        self.embedder = EmbeddingService()

    def get_categories(self, limit: int = 100):
        return self.repository.get_all(limit=limit)

    def get_category(self, category_id: int):
        return self.repository.get_by_id(category_id)

    def get_main_categories(self, limit: int = 100):
        return self.repository.get_main_categories(limit)

    def get_closest_categories(self, query: Union[str, List[float]], limit: int = 10):
        if isinstance(query, str):
            vector = self.embedder.embed_text(query)
        else:
            vector = query
        return self.repository.get_closest(vector, limit)


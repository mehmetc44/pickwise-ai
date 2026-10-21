import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from config import settings

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"

        model_path = settings.EMBEDDING_MODEL_PATH
        if not os.path.isabs(model_path):
            base_dir = Path(__file__).resolve().parent.parent
            model_path = str((base_dir / model_path).resolve())

        model_name = getattr(settings, "EMBEDDING_MODEL_NAME", "Trendyol/TY-ecomm-embed-multilingual-base-v1.2.0")
        
        self.model = SentenceTransformer(
            model_name,
            cache_folder=model_path,
            trust_remote_code=True,
        )

    def embed_text(self, text: str) -> list[float]:
        """Metni embedding vektörüne (list of float) dönüştürür."""
        embedding = self.model.encode(text, normalize_embeddings=True, show_progress_bar=False)
        return embedding.tolist()

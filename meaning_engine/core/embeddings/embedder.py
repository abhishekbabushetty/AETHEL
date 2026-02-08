from sentence_transformers import SentenceTransformer
from typing import List
import logging
from core.config import settings

logger = logging.getLogger("meaning_engine")

class Embedder:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Lazy load the model.
        """
        try:
            logger.info(f"Loading Embedding Model: {settings.EMBEDDING_MODEL}...")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding Model Loaded.")
        except Exception as e:
            logger.critical(f"Failed to load embedding model: {e}")
            raise

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        """
        if not texts:
            return []
            
        try:
            # batch_size=32 is standard default, can tune in config
            embeddings = self._model.encode(texts, batch_size=32, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

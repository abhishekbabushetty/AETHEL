from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
import logging
from core.config import settings

logger = logging.getLogger("meaning_engine")

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST, 
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.COLLECTION_NAME
        self._ensure_collection()

    def _ensure_collection(self):
        """
        Create collection if it doesn't exist.
        """
        try:
            collections = self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)
            
            if not exists:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384, # Match MiniLM-L6-v2
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            # Fail silently if Qdrant is not up (e.g. during build), but log it.
            logger.warning(f"Could not connect/create Qdrant collection: {e}")

    def upsert(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Uploads vectors and payload to Qdrant.
        """
        if not chunks or not embeddings:
            return

        points = []
        for i, chunk in enumerate(chunks):
            # Qdrant requires a payload dict
            payload = {
                "content": chunk["content"],
                "level": chunk["level"],
                "chunk_id": chunk["chunk_id"],
                **chunk["metadata"]
            }
            
            points.append(models.PointStruct(
                id=chunk["chunk_id"], # Can use hash or UUID if not string-compatible, but string works in recent Qdrant
                vector=embeddings[i],
                payload=payload
            ))

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Indexed {len(points)} chunks into {self.collection_name}")
        except Exception as e:
            logger.error(f"Indexing failed: {e}")

    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search.
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return [
                {"score": hit.score, "content": hit.payload.get("content"), "metadata": hit.payload}
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

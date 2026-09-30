import os
import pickle
from typing import List, Dict

import faiss
from sentence_transformers import SentenceTransformer

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class FaissStore:
    """Long-term (MAG) memory — embeds conversation turns and stores them for semantic recall."""

    def __init__(self):
        logger.info(f"Loading embedding model: {settings.embedding_model_name}")
        self.embedder = SentenceTransformer(settings.embedding_model_name)
        self.dimension = self.embedder.get_sentence_embedding_dimension()

        self.index_path = settings.faiss_index_path
        self.metadata_path = settings.faiss_metadata_path
        self.metadata: List[Dict[str, str]] = []

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            logger.info(f"Loaded FAISS index with {len(self.metadata)} memories")
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
            logger.info("Created new empty FAISS index")

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def add_memory(self, session_id: str, role: str, content: str) -> None:
        """Embed a turn and store it permanently."""
        try:
            vector = self.embedder.encode([content])
            self.index.add(vector)
            self.metadata.append({"session_id": session_id, "role": role, "content": content})
            self._save()
        except Exception as e:
            logger.error(f"FAISS add_memory failed: {e}")

    def search(self, query: str, k: int = None) -> List[str]:
        """Return the top-k most semantically relevant past turns for a query."""
        if len(self.metadata) == 0:
            return []

        k = k or settings.long_term_top_k
        k = min(k, len(self.metadata))

        try:
            query_vector = self.embedder.encode([query])
            distances, indices = self.index.search(query_vector, k)
            results = []
            for idx in indices[0]:
                if idx != -1:
                    entry = self.metadata[idx]
                    results.append(f"{entry['role']}: {entry['content']}")
            return results
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []


faiss_store = FaissStore()
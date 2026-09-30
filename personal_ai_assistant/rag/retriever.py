import os
import pickle
from typing import List, Dict

import faiss

from personal_ai_assistant.rag.document_loader import load_document
from personal_ai_assistant.rag.chunker import chunk_text
from personal_ai_assistant.rag.embedder import get_embedder, get_embedding_dimension
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class RagRetriever:
    """Document-based (RAG) retrieval — indexes documents and retrieves relevant chunks for a query."""

    def __init__(self):
        self.embedder = get_embedder()
        self.dimension = get_embedding_dimension()

        self.index_path = settings.rag_index_path
        self.metadata_path = settings.rag_metadata_path
        self.metadata: List[Dict[str, str]] = []

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            logger.info(f"Loaded RAG index with {len(self.metadata)} chunks")
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
            logger.info("Created new empty RAG index")

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def ingest_document(self, file_path: str) -> int:
        """Load, chunk, embed, and store a document. Returns the number of chunks added."""
        text = load_document(file_path)
        chunks = chunk_text(text)

        if not chunks:
            logger.info(f"No chunks produced from {file_path} (empty document?)")
            return 0

        vectors = self.embedder.encode(chunks)
        self.index.add(vectors)

        filename = os.path.basename(file_path)
        for chunk in chunks:
            self.metadata.append({"source": filename, "content": chunk})

        self._save()
        logger.info(f"Ingested {len(chunks)} chunks from {filename}")
        return len(chunks)

    def search(self, query: str, k: int = None) -> List[Dict[str, str]]:
        """Return the top-k most relevant chunks (with source filename) for a query."""
        if len(self.metadata) == 0:
            return []

        k = k or settings.rag_top_k
        k = min(k, len(self.metadata))

        try:
            query_vector = self.embedder.encode([query])
            distances, indices = self.index.search(query_vector, k)
            results = []
            for idx in indices[0]:
                if idx != -1:
                    results.append(self.metadata[idx])
            return results
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return []


rag_retriever = RagRetriever()
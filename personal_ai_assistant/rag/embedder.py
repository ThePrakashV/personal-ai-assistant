from sentence_transformers import SentenceTransformer

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

logger.info(f"Loading shared embedding model: {settings.embedding_model_name}")
_shared_embedder = SentenceTransformer(settings.embedding_model_name)


def get_embedder() -> SentenceTransformer:
    """Returns the shared embedding model instance (loaded once, reused everywhere)."""
    return _shared_embedder


def get_embedding_dimension() -> int:
    return _shared_embedder.get_sentence_embedding_dimension()
from typing import List

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks of roughly `chunk_size` characters."""
    chunk_size = settings.chunk_size
    overlap = settings.chunk_overlap

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap  # move forward, keeping some overlap

    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks
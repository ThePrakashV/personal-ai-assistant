import os

from pypdf import PdfReader
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def load_document(file_path: str) -> str:
    """Load a .pdf or .txt file and return its raw text content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document not found: {file_path}")

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return _load_pdf(file_path)
    elif extension == ".txt":
        return _load_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension} (only .pdf and .txt supported)")


def _load_pdf(file_path: str) -> str:
    logger.info(f"Loading PDF: {file_path}")
    reader = PdfReader(file_path)
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_parts)


def _load_txt(file_path: str) -> str:
    logger.info(f"Loading TXT: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
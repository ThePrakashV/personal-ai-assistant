from typing import Iterator, List, Dict

import ollama
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Wrapper around the Ollama client — single point of contact for the LLM engine."""

    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.model = settings.ollama_model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a full message list (system/history/user) and return the plain text reply."""
        try:
            response = self.client.chat(model=self.model, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise

    def chat_stream(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        """Send a full message list and yield the reply chunk by chunk."""
        try:
            stream = self.client.chat(model=self.model, messages=messages, stream=True)
            for part in stream:
                content = part.get("message", {}).get("content", "")
                if content:
                    yield content
        except Exception as e:
            logger.error(f"Ollama chat_stream failed: {e}")
            raise


ollama_client = OllamaClient()
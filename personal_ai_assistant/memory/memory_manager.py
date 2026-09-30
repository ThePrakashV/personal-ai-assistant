from typing import List, Dict

from personal_ai_assistant.memory.redis_cache import redis_cache
from personal_ai_assistant.memory.faiss_store import faiss_store
from personal_ai_assistant.rag.retriever import rag_retriever
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """Combines short-term memory (Redis/CAG), long-term memory (FAISS/MAG),
    and document retrieval (RAG) into one interface.
    """

    def build_messages(self, session_id: str, user_message: str) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []

        # Long-term conversation memories
        relevant_memories = faiss_store.search(user_message)
        if relevant_memories:
            context_note = "Relevant facts from earlier conversations:\n" + "\n".join(relevant_memories)
            messages.append({"role": "system", "content": context_note})

        # Document (RAG) chunks
        relevant_chunks = rag_retriever.search(user_message)
        if relevant_chunks:
            doc_note = "Relevant information from uploaded documents:\n" + "\n".join(
                f"[{c['source']}] {c['content']}" for c in relevant_chunks
            )
            messages.append({"role": "system", "content": doc_note})

        # Short-term recent history
        history = redis_cache.get_history(session_id)
        messages.extend(history)

        # New user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def save_turn(self, session_id: str, role: str, content: str) -> None:
        redis_cache.add_turn(session_id, role, content)
        faiss_store.add_memory(session_id, role, content)


memory_manager = MemoryManager()
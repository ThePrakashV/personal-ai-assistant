from typing import Iterator

from personal_ai_assistant.llm.ollama_client import ollama_client
from personal_ai_assistant.memory.memory_manager import memory_manager
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def generate_response(session_id: str, user_message: str) -> str:
    """Full (non-streaming) inference, memory-aware."""
    logger.info(f"Generating response for session {session_id}: {user_message[:50]}...")
    messages = memory_manager.build_messages(session_id, user_message)
    reply = ollama_client.chat(messages)

    memory_manager.save_turn(session_id, "user", user_message)
    memory_manager.save_turn(session_id, "assistant", reply)

    logger.info("Response generated successfully")
    return reply


def generate_response_stream(session_id: str, user_message: str) -> Iterator[str]:
    """Streaming inference, memory-aware. Saves the turn to memory once streaming completes."""
    logger.info(f"Streaming response for session {session_id}: {user_message[:50]}...")
    messages = memory_manager.build_messages(session_id, user_message)

    full_reply = ""
    for chunk in ollama_client.chat_stream(messages):
        full_reply += chunk
        yield chunk

    memory_manager.save_turn(session_id, "user", user_message)
    memory_manager.save_turn(session_id, "assistant", full_reply)

    logger.info("Streaming completed")
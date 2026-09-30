import json
from typing import List, Dict

import redis
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Short-term (CAG) memory — stores the last N turns of a conversation per session."""

    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )
        self.limit = settings.short_term_turns_limit

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}:history"

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        """Append a single turn (user or assistant message) to the session's short-term history."""
        try:
            key = self._key(session_id)
            turn = json.dumps({"role": role, "content": content})
            self.client.rpush(key, turn)
            self.client.ltrim(key, -self.limit, -1)  # keep only the last N turns
        except Exception as e:
            logger.error(f"Redis add_turn failed: {e}")

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Return the short-term history for a session as a list of {role, content} dicts."""
        try:
            key = self._key(session_id)
            raw_turns = self.client.lrange(key, 0, -1)
            return [json.loads(t) for t in raw_turns]
        except Exception as e:
            logger.error(f"Redis get_history failed: {e}")
            return []

    def clear_session(self, session_id: str) -> None:
        """Wipe the short-term history for a session (e.g. on explicit 'new chat')."""
        try:
            self.client.delete(self._key(session_id))
        except Exception as e:
            logger.error(f"Redis clear_session failed: {e}")


redis_cache = RedisCache()
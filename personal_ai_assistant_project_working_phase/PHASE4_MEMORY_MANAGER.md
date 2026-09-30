# Phase 4: Memory Manager (Short-term Cache + Long-term Memory)

## Status: ✅ Complete
**Date:** 20-09-2026 to 21-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 3 vare namma assistant-ku memory illa — ovvoru message "puthu conversation" maadhiri treat aagுchu. Phase 4 la **two-tier memory system** build pண்ணினோம்:

1. **CAG (Cache-Augmented / Short-term Memory)** — Redis use pண்ணி, oru session-oda last N messages (default 10) fast ah store pண்ணி retrieve pண்ணும்.
2. **MAG (Memory-Augmented / Long-term Memory)** — FAISS (vector database) + Sentence-Transformers use pண்ணி, ella conversation turns-um permanent ah embed pண்ணி disk la store pண்ணும். Semantic search மூலமா, exact words illainaாlும் "meaning" match aana pழைya memories-a தேடி எடுக்கும்.
3. `memory_manager.py` — CAG + MAG rendையும் ஒன்றாக இணைத்து, LLM-ku anுப்ப munnadi combined context build pண்ணும்.
4. `ollama_client.py` matrum `inference.py` — single-string input-la irundhு **full messages list** (system context + short-term history + new message) support pண்ண update pண்ணினோம்.
5. `websocket.py` — per-client `session_id` support add pண்ணினோம் (UUID-based, client-ku anுப்பப்படும்).
6. `test_client.html` — `session_id`-a `localStorage` la persist pண்ணும்படி update pண்ணினோம் (browser refresh aanaாlும் same session continue aagும்).
7. Redis (Docker), FAISS index, matrum end-to-end memory recall — ellame **rigorously test pண்ணி** confirm pண்ணினோம், including oru **language confusion issue** (Tanglish input) matrum oru **Docker container restart issue** debug pண்ணி fix pண்ணினோம்.

**Result:** Assistant ippo namma name/location maadhiri facts-a **same session-lum** (CAG), **future sessions-lum, server restart aanaாலும்** (MAG) ninaikkuthு. Idhே confirmed pண்ணப்பட்டadhு rendு separate tests-la — Redis FLUSHALL pண்ணின apparam-um "What is my name?" correct ah answer வந்தது, idhு MAG mattும் exclusive ah work pண்ணிyachu nு proof.

---

## 2. Full Folder Structure (Phase 4 end state — new/updated marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── utils\
│   │   ├── __init__.py
│   │   ├── config.py               ← UPDATED (memory settings added)
│   │   ├── logger.py
│   │   └── helpers.py
│   ├── llm\
│   │   ├── __init__.py
│   │   ├── ollama_client.py        ← UPDATED (messages list support)
│   │   └── inference.py            ← UPDATED (memory-aware, session_id)
│   ├── memory\                     ← NEW (Phase 4)
│   │   ├── __init__.py
│   │   ├── redis_cache.py          ← NEW (CAG)
│   │   ├── faiss_store.py          ← NEW (MAG)
│   │   └── memory_manager.py       ← NEW (orchestration)
│   └── api\
│       ├── __init__.py
│       ├── main.py
│       ├── routes.py
│       ├── schemas.py
│       └── websocket.py            ← UPDATED (session_id support)
├── data\                           ← NEW (FAISS index storage)
│   ├── faiss_memory.index
│   └── faiss_metadata.pkl
├── venv\                          (excluded from git)
├── requirements.txt                ← UPDATED (redis, faiss-cpu, sentence-transformers)
├── test_client.html                ← UPDATED (session_id persistence)
├── setup.py
├── pyproject.toml
├── .env                           (excluded from git)
├── .gitignore
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Redis Server Setup (Docker)
```
docker run -d --name redis-mem -p 6379:6379 redis
docker ps
```

### Step 2 — Create `memory/` Package
```
mkdir personal_ai_assistant\memory
type nul > personal_ai_assistant\memory\__init__.py
type nul > personal_ai_assistant\memory\redis_cache.py
type nul > personal_ai_assistant\memory\faiss_store.py
type nul > personal_ai_assistant\memory\memory_manager.py
```

### Step 3 — Update Dependencies
```
pip install -r requirements.txt --prefer-binary
```

### Step 4 — Create Data Folder (for FAISS index)
```
mkdir data
```

### Step 5 — Verify Every File Before Running
```
python -m py_compile personal_ai_assistant\utils\config.py
python -m py_compile personal_ai_assistant\memory\redis_cache.py
python -m py_compile personal_ai_assistant\memory\faiss_store.py
python -m py_compile personal_ai_assistant\memory\memory_manager.py
python -m py_compile personal_ai_assistant\llm\ollama_client.py
python -m py_compile personal_ai_assistant\llm\inference.py
python -m py_compile personal_ai_assistant\api\websocket.py
```

### Step 6 — Run Server and Test Short-term Memory (CAG)
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```
(Test via `test_client.html` — see Section 6 for results.)

### Step 7 — Test Long-term Memory (MAG) — Clear Redis, Verify FAISS-only Recall
```
docker exec -it redis-mem redis-cli FLUSHALL
```
(Then re-test the same query via `test_client.html` without restarting FastAPI.)

### Step 8 — Fix: Redis Container Not Auto-starting After Docker Desktop Restart
```
docker start redis-mem
docker ps
docker update --restart unless-stopped redis-mem
```

---

## 4. Full File Contents (Final Working Code)

### `requirements.txt`
**Path:** `D:\project\personal_ai_assistant_project\requirements.txt`
```
fastapi
uvicorn
pydantic
pydantic-settings
python-dotenv
ollama
websockets
redis
faiss-cpu
sentence-transformers
```

---

### `personal_ai_assistant\utils\config.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\utils\config.py`

**Purpose:** Added Redis (CAG) and FAISS (MAG) settings alongside existing LLM/server settings.

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Personal AI Assistant"

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # Short-term memory (Redis / CAG)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    short_term_turns_limit: int = 10  # last N messages (user+assistant combined)

    # Long-term memory (FAISS / MAG)
    embedding_model_name: str = "all-MiniLM-L6-v2"
    faiss_index_path: str = "data/faiss_memory.index"
    faiss_metadata_path: str = "data/faiss_metadata.pkl"
    long_term_top_k: int = 3  # how many relevant memories to retrieve

    class Config:
        env_file = ".env"


settings = Settings()
```

---

### `personal_ai_assistant\memory\redis_cache.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\memory\redis_cache.py`

**Purpose:** Short-term (CAG) memory — stores the last N turns of a conversation per session using a Redis list, auto-trimmed to the configured limit.

```python
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
```

---

### `personal_ai_assistant\memory\faiss_store.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\memory\faiss_store.py`

**Purpose:** Long-term (MAG) memory — embeds every conversation turn with Sentence-Transformers and stores it in a FAISS vector index (persisted to disk), enabling semantic recall across sessions and server restarts.

```python
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
```

---

### `personal_ai_assistant\memory\memory_manager.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\memory\memory_manager.py`

**Purpose:** Combines CAG (Redis) and MAG (FAISS) into a single interface — builds the full message list sent to the LLM, and saves each turn to both memory layers.

```python
from typing import List, Dict

from personal_ai_assistant.memory.redis_cache import redis_cache
from personal_ai_assistant.memory.faiss_store import faiss_store
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """Combines short-term (Redis/CAG) and long-term (FAISS/MAG) memory into one interface."""

    def build_messages(self, session_id: str, user_message: str) -> List[Dict[str, str]]:
        """Build the full message list to send to the LLM: relevant long-term facts
        (as a system note) + recent short-term history + the new user message.
        """
        messages: List[Dict[str, str]] = []

        # Long-term relevant memories → injected as a system-style context note
        relevant_memories = faiss_store.search(user_message)
        if relevant_memories:
            context_note = "Relevant facts from earlier conversations:\n" + "\n".join(relevant_memories)
            messages.append({"role": "system", "content": context_note})

        # Short-term recent history
        history = redis_cache.get_history(session_id)
        messages.extend(history)

        # New user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def save_turn(self, session_id: str, role: str, content: str) -> None:
        """Persist a turn to both short-term (Redis) and long-term (FAISS) memory."""
        redis_cache.add_turn(session_id, role, content)
        faiss_store.add_memory(session_id, role, content)


memory_manager = MemoryManager()
```

---

### `personal_ai_assistant\llm\ollama_client.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\llm\ollama_client.py`

**Purpose:** Updated to accept a full `messages` list (system context + history + new message) instead of a single string, so memory context can be passed to the model.

```python
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
```

---

### `personal_ai_assistant\llm\inference.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\llm\inference.py`

**Purpose:** Now memory-aware — builds messages via `memory_manager`, calls the LLM, and saves both the user message and the assistant's reply back into memory.

```python
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
```

---

### `personal_ai_assistant\api\websocket.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\websocket.py`

**Purpose:** Added per-client `session_id` — generated as a UUID if the client doesn't provide one, sent back to the client so it can persist it (e.g. in `localStorage`).

```python
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from personal_ai_assistant.llm.inference import generate_response_stream
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    session_id = websocket.query_params.get("session_id") or str(uuid.uuid4())
    logger.info(f"WebSocket client connected — session_id: {session_id}")

    await websocket.send_json({"type": "session", "content": session_id})

    try:
        while True:
            user_message = await websocket.receive_text()

            if not user_message.strip():
                await websocket.send_json({"type": "error", "content": "Message cannot be empty"})
                continue

            logger.info(f"WS received [{session_id}]: {user_message[:50]}...")

            try:
                for chunk in generate_response_stream(session_id, user_message):
                    await websocket.send_json({"type": "chunk", "content": chunk})

                await websocket.send_json({"type": "done"})

            except Exception as e:
                logger.error(f"WS inference failed: {e}")
                await websocket.send_json({"type": "error", "content": "LLM failed to generate a response"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected — session_id: {session_id}")
```

---

### `test_client.html` (Testing Tool)
**Path:** `D:\project\personal_ai_assistant_project\test_client.html`

**Purpose:** Added `localStorage`-based session persistence, so refreshing the browser keeps the same `session_id` and the same memory context.

```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test Client</title>
</head>
<body>
    <h2>Personal AI Assistant — WebSocket Test</h2>
    <p>Session ID: <span id="sessionDisplay">connecting...</span></p>
    <input type="text" id="msgInput" placeholder="Type your message" size="50">
    <button onclick="sendMessage()">Send</button>
    <pre id="output" style="border:1px solid #ccc; padding:10px; min-height:100px; white-space:pre-wrap;"></pre>

    <script>
        let storedSessionId = localStorage.getItem("session_id") || "";
        const wsUrl = storedSessionId
            ? `ws://localhost:8000/ws/chat?session_id=${storedSessionId}`
            : `ws://localhost:8000/ws/chat`;

        const socket = new WebSocket(wsUrl);
        const output = document.getElementById("output");
        const sessionDisplay = document.getElementById("sessionDisplay");

        socket.onopen = () => {
            output.textContent += "[Connected]\n";
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "session") {
                localStorage.setItem("session_id", data.content);
                sessionDisplay.textContent = data.content;
            } else if (data.type === "chunk") {
                output.textContent += data.content;
            } else if (data.type === "done") {
                output.textContent += "\n[Done]\n\n";
            } else if (data.type === "error") {
                output.textContent += "\n[Error: " + data.content + "]\n\n";
            }
        };

        socket.onclose = () => {
            output.textContent += "\n[Disconnected]\n";
        };

        function sendMessage() {
            const input = document.getElementById("msgInput");
            output.textContent += "\n> " + input.value + "\n";
            socket.send(input.value);
            input.value = "";
        }
    </script>
</body>
</html>
```

---

## 5. Errors Faced & How We Solved Them

### Error 1: Tanglish input confused the LLM, producing wrong-language / wrong-context replies

**Exact input tested:** `"en peru prakash ennoda gf name reena"`

**What happened:** Instead of understanding this as "my name is Prakash, my girlfriend's name is Reena", `llama3.2` misread "Prakash" and "Reena" as unrelated names, and replied **entirely in Spanish**, asking about "Prakash Ennoda" and "Reena" as if they were strangers, even referencing an unrelated real person ("Prakash Karat", a political figure) based on loose name similarity.

**Karanam (Root Cause):** Idhu **memory system-oda bug illa**. `llama3.2` base model-kku Tanglish (Tamil vaartaigal English letters-la) **reliably purinjukka theriyாthu** — training data la idhு pattern konjam mattume irundhirukalாm், adhான் misinterpret pண்ணிyachu. Namma Redis/FAISS code correct ah run aachu (logs clean ah irundhuchu) — aana **wrong extracted meaning** thான் memory-la store aachu.

**Analogy:** Waiter (memory system) order-a correct ah kitchen-ku (storage) kொண்டு pогிduthu, aana chef-kku (LLM) andha language puriyாthadhால், order-yE wrong ah puriunthu.

**Fix:** Testing-a **plain English**-la retry pண்ணினோம்: `"My name is Prakash and I live in Chennai"` → idhு correct ah understood aachu, matrum memory recall accurate ah work pண்ணிyachu.

**Status:** ✅ Worked around by testing in English. **Not fixed at the code level** — if Tanglish/multilingual support is needed later, a system prompt enforcing "respond only in English" or a stronger multilingual model can be considered in a future phase.

---

### Error 2: Model occasionally replied in Spanish even for English input

**What happened:** Even with English input ("My name is Prakash and I live in Chennai", "What is my name?"), `llama3.2` sometimes replied in **Spanish** instead of English.

**Karanam (Root Cause):** This is a known quirk of small open-source LLMs like `llama3.2` — occasional random language-switching, especially when the model's internal "confidence" about language context is low. Not related to our memory implementation.

**Status:** ⚠️ Noted, not fixed — memory recall was still factually correct despite the language switch (e.g., "Tu nombre es Prakash" — Spanish for "Your name is Prakash" — was still the right answer). Can optionally be addressed later with a system prompt like `"Always respond in English."` if needed.

---

### Error 3: Docker container `redis-mem` not running after a fresh restart

**Exact error seen:**
```
Error response from daemon: container 194c4576466820c98e440ab161251e781e2dee5ed079de08fbfd522ed9af7353 is not running
```
(when running `docker exec -it redis-mem redis-cli FLUSHALL`)

**Karanam (Root Cause):** After stopping and restarting Docker Desktop (or the machine) on a new day, Docker containers **do not auto-start by default** unless they were created with a restart policy. `redis-mem` was originally run with a plain `docker run` (no `--restart` flag), so it stayed in a stopped state.

**Analogy:** Notepad (Redis) drawer got locked when the room (Docker Desktop) restarted — commands can't reach it until the drawer is unlocked (container started) again.

**Fix:**
```
docker start redis-mem
docker ps    # confirm "Up" status
```
Then, to prevent this from happening again:
```
docker update --restart unless-stopped redis-mem
```
This sets a restart policy so `redis-mem` will automatically start whenever Docker Desktop starts, from now on.

**Status:** ✅ Resolved — container started manually this time, and future restarts are now automatic due to the applied restart policy.

---

## 6. Verified Test Results (Screenshots Confirmed)

### Test 1: Redis Container Health
```
docker ps
```
Confirmed `redis-mem` container `Up` and healthy on port `6379`.

### Test 2: Short-term Memory (CAG) — Same Session
| Step | Input | Result |
|---|---|---|
| 1 | `My name is Prakash and I live in Chennai` | Acknowledged (in Spanish, see Error 2) |
| 2 | `what is my name` (same session, same tab) | ✅ Correctly recalled: "Tu nombre es Prakash" (Your name is Prakash) |

### Test 3: Long-term Memory (MAG) — Exclusive Test (Redis Cleared)
| Step | Action | Result |
|---|---|---|
| 1 | `docker exec -it redis-mem redis-cli FLUSHALL` | Returned `OK` — Redis short-term memory fully wiped |
| 2 | Same browser tab, same session, no FastAPI restart: `what is my name` | ✅ "We've had this conversation before, Prakash! You've told me that your name is Prakash." |

**Confirmed:** Since Redis was completely empty at this point, this answer could only have come from **FAISS (MAG) semantic search** — proving long-term memory works independently of short-term cache.

---

## 7. Important Notes for Future Reference

- ⚠️ **Redis container does not auto-start on its own** unless a restart policy is set — now fixed with `docker update --restart unless-stopped redis-mem`, but worth remembering for any *new* containers added in later phases (e.g. if a separate DB container is added).
- ⚠️ **Tanglish input is not reliably understood by `llama3.2`** — for testing memory/logic features going forward, prefer plain English to avoid confounding "is this a memory bug or a language bug" debugging.
- The model occasionally replies in a non-English language (observed: Spanish) even for English input — this is a base model quirk, not a code issue. Can be constrained later via a system prompt if consistency is required.
- `memory_manager.build_messages()` always injects FAISS results as a `system` role message — if `llama3.2` starts ignoring this context in future testing, consider rephrasing the injected note or trying a different embedding/top_k value in `config.py`.
- First-time run of `faiss_store.py` downloads the `all-MiniLM-L6-v2` embedding model (~80MB) — needs internet once; fully offline afterward.
- `data/faiss_memory.index` and `data/faiss_metadata.pkl` grow over time as more turns are saved — no cleanup/expiry logic exists yet; consider this for a future phase if long-term storage size becomes a concern.
- Both `docker ps` and `ollama list` should be checked every time the project is resumed after a break (new day), since neither Docker containers nor the Ollama service are guaranteed to persist across full machine restarts.

---

## 8. Next Phase

**Phase 5: RAG Pipeline** — Document Loader → Chunker → Embedder (Sentence-Transformers, already available from Phase 4) → FAISS Retriever, so the assistant can answer questions using uploaded documents (PDFs, text files) in addition to conversational memory.

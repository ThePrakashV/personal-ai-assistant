# Phase 5: RAG Pipeline (Document Loader → Chunker → Embedder → Retriever)

## Status: ✅ Complete
**Date:** 22-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 4 la assistant-kku **conversation memory** irundhுchu (namma pேsina facts). Phase 5 la assistant-kku **document-based knowledge** add pண்ணினோம் — RAG (Retrieval-Augmented Generation):

1. Puthusа `rag/` package create pண்ணினோம் — `document_loader.py` (PDF/TXT read pண்ண), `chunker.py` (periya text-a chinna pieces ah split pண்ண), `embedder.py` (shared embedding model, memory matrum RAG rendும் reuse pண்ணும்), `retriever.py` (document indexing + semantic search — Phase 4-oda `faiss_store.py` maadhiri structure, aana separate index).
2. `requirements.txt` la `pypdf` (PDF reading) matrum `python-multipart` (file upload support) add pண்ணினோம்.
3. `utils/config.py` la RAG-specific settings add pண்ணினோம் (documents folder, chunk size/overlap, top_k).
4. `memory/memory_manager.py`-a update pண்ணி, conversation memory (Phase 4) + document chunks (Phase 5) rendையும் sேர்th்து LLM-ku context ah anுப்ப pண்ணினோம்.
5. `api/schemas.py` la `IngestResponse` add pண்ணினோம், `api/routes.py` la `POST /documents/upload` endpoint add pண்ணினோம்.
6. Test document (`company_policy.txt`) create pண்ணி, upload pண்ணி, endsto-end ah **document-based question** kேttа correct ah answer varுதா nு confirm pண்ணினோம்.
7. Journey-la **4 separate issues** debug pண்ணி fix pண்ணினோம் — missing `python-multipart` dependency, browser la `0.0.0.0` vs `localhost` confusion, server/curl-a same CMD window-la run pண்ண try pண்ணின mistake, matrும் laptop restart apparam ella services-um puthுsa start pண்ண வேண்டிய steps.

**Result:** Namma AI Assistant ippo **three-layer intelligence** vachirukku — (1) LLM-oda general knowledge, (2) conversation memory (Phase 4 — CAG+MAG), (3) uploaded documents (Phase 5 — RAG). Confirmed test: "What database is used for short-term memory in this project?" nு kேttа, assistant `company_policy.txt`-la irundhு **"Redis"** nு correct ah, semantic search மூலமா answer pண்ணிyachu.

---

## 2. Full Folder Structure (Phase 5 end state — new/updated marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── utils\
│   │   ├── __init__.py
│   │   ├── config.py               ← UPDATED (RAG settings added)
│   │   ├── logger.py
│   │   └── helpers.py
│   ├── llm\
│   │   ├── __init__.py
│   │   ├── ollama_client.py
│   │   └── inference.py
│   ├── memory\
│   │   ├── __init__.py
│   │   ├── redis_cache.py
│   │   ├── faiss_store.py
│   │   └── memory_manager.py       ← UPDATED (RAG context added)
│   ├── rag\                        ← NEW (Phase 5)
│   │   ├── __init__.py
│   │   ├── document_loader.py      ← NEW
│   │   ├── chunker.py              ← NEW
│   │   ├── embedder.py             ← NEW
│   │   └── retriever.py            ← NEW
│   └── api\
│       ├── __init__.py
│       ├── main.py
│       ├── routes.py                ← UPDATED (/documents/upload added)
│       ├── schemas.py               ← UPDATED (IngestResponse added)
│       └── websocket.py
├── data\
│   ├── documents\                  ← NEW (uploaded documents storage)
│   │   └── company_policy.txt      ← NEW (test document)
│   ├── faiss_memory.index          (Phase 4 — conversation memory)
│   ├── faiss_metadata.pkl          (Phase 4 — conversation memory)
│   ├── rag_index.index             ← NEW (Phase 5 — document index)
│   └── rag_metadata.pkl            ← NEW (Phase 5 — document index)
├── venv\                          (excluded from git)
├── requirements.txt                ← UPDATED (pypdf, python-multipart added)
├── test_client.html
├── setup.py
├── pyproject.toml
├── .env                           (excluded from git)
├── .gitignore
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Create `rag/` Package
```
mkdir personal_ai_assistant\rag
type nul > personal_ai_assistant\rag\__init__.py
type nul > personal_ai_assistant\rag\document_loader.py
type nul > personal_ai_assistant\rag\chunker.py
type nul > personal_ai_assistant\rag\embedder.py
type nul > personal_ai_assistant\rag\retriever.py
mkdir data\documents
```

### Step 2 — Update Dependencies
```
pip install -r requirements.txt --prefer-binary
```

### Step 3 — Verify Every File Before Running
```
python -m py_compile personal_ai_assistant\utils\config.py
python -m py_compile personal_ai_assistant\rag\document_loader.py
python -m py_compile personal_ai_assistant\rag\chunker.py
python -m py_compile personal_ai_assistant\rag\embedder.py
python -m py_compile personal_ai_assistant\rag\retriever.py
python -m py_compile personal_ai_assistant\memory\memory_manager.py
python -m py_compile personal_ai_assistant\api\schemas.py
python -m py_compile personal_ai_assistant\api\routes.py
```

### Step 4 — Create Test Document
```
notepad data\documents\company_policy.txt
```

### Step 5 — Run Server (first attempt — hit missing dependency error, see Section 5)
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6 — Fix: Install Missing File Upload Dependency
```
pip install python-multipart --prefer-binary
```

### Step 7 — Re-run Server (in its own dedicated CMD window, kept open)
```
cd D:\project\personal_ai_assistant_project
venv\Scripts\activate
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 8 — Upload Document (in a SEPARATE second CMD window)
```
cd D:\project\personal_ai_assistant_project
curl -X POST http://localhost:8000/documents/upload -F "file=@data/documents/company_policy.txt"
```

### Step 9 — Test Retrieval
Via `test_client.html` (opened with `http://localhost:8000`, not `0.0.0.0:8000`):
```
What database is used for short-term memory in this project?
```

### Step 10 — After Laptop Restart (documented for future reference)
```
# 1. Start Docker Desktop (wait for full load)
docker ps

# 2. Check Ollama
ollama list

# 3. Navigate + activate venv
cd D:\project\personal_ai_assistant_project
venv\Scripts\activate

# 4. Run server
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000

# 5. Open test_client.html in browser using localhost:8000 (not 0.0.0.0)
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
pypdf
python-multipart
```

---

### `personal_ai_assistant\utils\config.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\utils\config.py`

**Purpose:** Added RAG-specific settings (documents folder, chunk size/overlap, retrieval top_k) alongside existing LLM/server/memory settings.

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
    short_term_turns_limit: int = 10

    # Long-term memory (FAISS / MAG)
    embedding_model_name: str = "all-MiniLM-L6-v2"
    faiss_index_path: str = "data/faiss_memory.index"
    faiss_metadata_path: str = "data/faiss_metadata.pkl"
    long_term_top_k: int = 3

    # RAG (documents)
    documents_folder: str = "data/documents"
    rag_index_path: str = "data/rag_index.index"
    rag_metadata_path: str = "data/rag_metadata.pkl"
    chunk_size: int = 500
    chunk_overlap: int = 50
    rag_top_k: int = 3

    class Config:
        env_file = ".env"


settings = Settings()
```

---

### `personal_ai_assistant\rag\document_loader.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\rag\document_loader.py`

**Purpose:** Loads `.pdf` or `.txt` files and returns their raw text content, for downstream chunking and embedding.

```python
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
```

---

### `personal_ai_assistant\rag\chunker.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\rag\chunker.py`

**Purpose:** Splits loaded text into overlapping chunks (default 500 chars, 50-char overlap) so the LLM/embedder can work with manageable pieces without losing meaning at chunk boundaries.

```python
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
        start += chunk_size - overlap

    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks
```

---

### `personal_ai_assistant\rag\embedder.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\rag\embedder.py`

**Purpose:** Provides a single shared `SentenceTransformer` instance so both memory (Phase 4) and RAG (Phase 5) can reuse the same loaded model instead of duplicating it in memory.

```python
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
```

**Note:** `memory/faiss_store.py` (Phase 4) still loads its own separate `SentenceTransformer` instance rather than using this shared one — left as-is to avoid touching stable Phase 4 code; noted as a possible future cleanup.

---

### `personal_ai_assistant\rag\retriever.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\rag\retriever.py`

**Purpose:** Document indexing and retrieval — mirrors the structure of `memory/faiss_store.py` (Phase 4) but uses a separate FAISS index dedicated to document chunks, keeping conversation memory and document knowledge cleanly separated.

```python
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
```

---

### `personal_ai_assistant\memory\memory_manager.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\memory\memory_manager.py`

**Purpose:** Now combines three sources into the LLM's context — long-term conversation memory (Phase 4), document chunks (Phase 5), and short-term recent history (Phase 4).

```python
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
```

---

### `personal_ai_assistant\api\schemas.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\schemas.py`

**Purpose:** Added `IngestResponse` for the document upload endpoint's response shape.

```python
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class IngestResponse(BaseModel):
    filename: str
    chunks_added: int
```

---

### `personal_ai_assistant\api\routes.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\routes.py`

**Purpose:** Added `POST /documents/upload` — accepts a `.pdf` or `.txt` file, saves it to `data/documents/`, and ingests it into the RAG index (load → chunk → embed → store).

```python
import os
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File

from personal_ai_assistant.api.schemas import ChatRequest, ChatResponse, IngestResponse
from personal_ai_assistant.llm.inference import generate_response
from personal_ai_assistant.rag.retriever import rag_retriever
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        reply = generate_response("default-session", request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="LLM failed to generate a response")


@router.post("/documents/upload", response_model=IngestResponse)
def upload_document(file: UploadFile = File(...)):
    allowed_extensions = (".pdf", ".txt")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    os.makedirs(settings.documents_folder, exist_ok=True)
    save_path = os.path.join(settings.documents_folder, file.filename)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks_added = rag_retriever.ingest_document(save_path)
        return IngestResponse(filename=file.filename, chunks_added=chunks_added)

    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document")
```

**Note:** `/chat` REST endpoint now uses a fixed `"default-session"` session_id so it can also benefit from memory/RAG context. Primary real-time chat remains the WebSocket (`/ws/chat`) endpoint.

---

### `data\documents\company_policy.txt` (Test Document)
**Path:** `D:\project\personal_ai_assistant_project\data\documents\company_policy.txt`

```
Personal AI Assistant - Internal Notes

The project uses Ollama with the llama3.2 model for all inference.
Short-term memory is handled by Redis, running in a Docker container named redis-mem.
Long-term memory and document retrieval both use FAISS vector indexes stored in the data folder.
The WebSocket endpoint for real-time chat is located at /ws/chat.
Document uploads are handled at /documents/upload, supporting PDF and TXT files only.
```

---

## 5. Errors Faced & How We Solved Them

### Error 1: `RuntimeError: Form data requires "python-multipart" to be installed`

**Exact error seen:**
```
File "...fastapi\dependencies\utils.py", line 129, in ensure_multipart_is_installed
    raise RuntimeError(multipart_not_installed_error) from None
RuntimeError: Form data requires "python-multipart" to be installed.
You can install "python-multipart" with:

pip install python-multipart
```

**Karanam (Root Cause):** `POST /documents/upload` endpoint **file upload** (`UploadFile = File(...)`) handle pண்ண, FastAPI-kku `python-multipart` library thேவை — idhு base FastAPI install-la include aagாthு, separate ah install pண்ணணும். Idhை install pண்ணாthதால், server **startup-லேயே crash** aachu (route registration time-la itself error throw pண்ணிyachு).

**Analogy:** "File upload counter" (endpoint) build pண்ணிடுchு, aana andha counter-la files unpack pண்ண thேவையாна tool (multipart parser) illa. Adhான் server start aagும்போதே crash aaguthு.

**Fix:**
```
pip install python-multipart --prefer-binary
```
matrum `requirements.txt` la add pண்ணினோம்.

**Status:** ✅ Resolved — server clean ah start aachu appuram, FAISS memory index (22 memories) matrum RAG index rendும் load aagi confirm aachu.

---

### Error 2: `curl: (7) Failed to connect to localhost:8000` even though server was "running"

**What happened:** Server run pண்ணிyிருந்தும், curl command **connect aagவில்லை** — first `Failed to connect` error, appuram browser la `0.0.0.0:8000` type pண்ணி test pண்ணின apparam-um issue continue aachu.

**Karanam (Root Cause) — rendு separate issues sேர்th்து irundhுchu:**

1. **`0.0.0.0` browser-la use pண்ண கூடாது:** `--host 0.0.0.0` nு solradhு server-ku "ella network interfaces-லேயும் listen pண்ணு" nு address. Idhு browser/curl-ku kொடுக்க கூடாது — browser la eppovும் `localhost` illa `127.0.0.1` use pண்ணணும்.

2. **Server matrum curl-a same CMD window-la run pண்ண try pண்ணின mistake:** Server oru window la `--reload` mode la foreground-la run aagும்போது, andha window andha process-ku **busy** ah irukும். Vேறே command (curl) அதே window-la type pண்ணினா, server process control-a vாnga முடியாது.

**Analogy:** Restaurant (server) திறந்து இருந்தாலும், delivery driver (curl) **wrong address** (`0.0.0.0`) ku poனா, delivery fail aagும். Matrும், waiter (CMD window) already customer order (`uvicorn --reload`) handle pண்ணிkkொண்டிருக்கும்போது, **அதே waiter-கிட்டேயே** vேறே task (curl) கொடுத்தா, வேலை செய்ய முடியாது.

**Fix:**
- Browser/curl la eppovும் **`http://localhost:8000`** use pண்ணுங்க, `0.0.0.0` alla.
- Server-a **oru dedicated CMD window** la run pண்ணி, **அப்படியே திறந்தே வையுங்க**. Curl/testing commands **rendாவது, separate CMD window** la run pண்ணுங்க.

**Status:** ✅ Resolved — rendு issues-um fix pண்ணின apparam, curl `{"filename":"company_policy.txt","chunks_added":1}` successfully return pண்ணிyachu.

---

### Error 3: Redis connection refused after laptop restart

**Exact error seen (in server logs):**
```
personal_ai_assistant.memory.redis_cache | ERROR | Redis get_history failed: 
Error 10061 connecting to localhost:6379. No connection could be made because the target machine actively refused it.
```

**Karanam (Root Cause):** Laptop restart aana apparam, **Docker Desktop** (matrும் adhுoda ella containers-um, including `redis-mem`) **automatic ah start aagவில்லை** — Docker Desktop itself open pண்ணப்படாதவரை, container-oda `unless-stopped` restart policy trigger aagாthு (andha policy Docker Desktop-a already running irukும்போது container-a mattும் auto-restart pண்ணும், Docker Desktop itself-a launch pண்ணாthு).

**Important note:** Idhு **full app crash illa** — WebSocket connection, LLM inference, matrும் FAISS long-term memory (MAG) ellame **normal ah continue aachு** (`try/except` error handling namma Phase 4 code-la already irundhுchு). "Where do I live?" nு kேttа correct ah "Chennai" nு FAISS-la irundhு answer வந்திருச்சு, Redis mattும் temporarily unavailable ah irundhுchு.

**Fix:**
1. Docker Desktop app-a manually open pண்ணுங்க
2. `docker ps` mூலமா `redis-mem` "Up" status verify pண்ணுங்க (Docker Desktop start aana udан, `unless-stopped` policy container-a automatic ah start pண்ணிyachு)

**Status:** ✅ Resolved — recorded as a standard step in the "after laptop restart" checklist (Section 3, Step 10) for all future sessions.

---

## 6. Verified Test Results (Screenshots Confirmed)

### Test 1: Document Upload
**Command:**
```
curl -X POST http://localhost:8000/documents/upload -F "file=@data/documents/company_policy.txt"
```
**Response:**
```json
{"filename":"company_policy.txt","chunks_added":1}
```

### Test 2: RAG Retrieval — Document-based Question
**Query (via `test_client.html`):**
```
What database is used for short-term memory in this project?
```
**Response:**
> "According to the uploaded document, Redis is used for short-term memory in this project. Specifically, it mentions that Redis is used as a short-term memory handler, running in a Docker container named `redis-mem`."

**Confirmed:** This answer could only have come from the uploaded document — it was not part of the current session's conversation history, proving the RAG retrieval pipeline (Loader → Chunker → Embedder → FAISS Retriever) works end-to-end.

### Test 3: Post-Restart Service Recovery
- Docker Desktop restarted → `redis-mem` auto-started via `unless-stopped` policy → `docker ps` confirmed "Up"
- FastAPI server restarted cleanly, reloaded FAISS memory index (22 memories) and RAG index
- Confirmed both memory (Phase 4) and RAG (Phase 5) indexes persisted correctly across the restart, since both are saved to disk (`data/` folder)

---

## 7. Important Notes for Future Reference

- ⚠️ **Always use `http://localhost:8000` in the browser/curl** — never `0.0.0.0:8000`. `0.0.0.0` is only valid as the `--host` value passed to uvicorn.
- ⚠️ **Server must run in its own dedicated CMD window, left open** — testing commands (curl, other CLI tools) always go in a **separate** second CMD window.
- ⚠️ **`python-multipart` is mandatory** for any FastAPI endpoint using `UploadFile`/`File()` — now in `requirements.txt` permanently for this project.
- ⚠️ **After every laptop/Docker Desktop restart**, follow the checklist in Section 3, Step 10 — Docker Desktop won't auto-launch itself even with `unless-stopped` set on individual containers.
- Both the RAG index (`data/rag_index.index`) and the memory index (`data/faiss_memory.index`) are **separate files** — conversation facts and document knowledge never mix, even though they use the same underlying FAISS + Sentence-Transformers technology.
- The RAG index persists across server restarts (saved to disk after every `ingest_document()` call) — documents only need to be uploaded once, not re-uploaded each session.
- Current chunking is simple character-based splitting (500 chars, 50 overlap) — works fine for small test documents; larger/more complex documents in later phases may benefit from smarter (sentence-aware or paragraph-aware) chunking if retrieval quality becomes an issue.
- `/documents/upload` currently only supports `.pdf` and `.txt` — expanding to `.docx`, `.md`, etc. can be considered later if needed.

---

## 8. Next Phase

**Phase 6: LangChain/LangGraph Agent Workflow** — introduce tool-calling and decision routing so the assistant can choose between plain chat, memory recall, document retrieval, and (in later phases) external tools, instead of always blending everything into one context.

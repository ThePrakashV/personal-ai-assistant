# Phase 2: Core LLM Engine (Ollama Integration)

## Status: ✅ Complete
**Date:** 20-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 1 la kattina foundation-oda மேல, ippo **LLM Engine** (namma project-oda "brain") connect pண்ணினோம்:

1. Puthusa `llm/` package create pண்ணினோம் — `ollama_client.py` (Ollama connection wrapper) matrum `inference.py` (core inference logic).
2. `requirements.txt` la `ollama` Python SDK add pண்ணி install pண்ணினோம்.
3. `api/schemas.py` la `ChatRequest` / `ChatResponse` Pydantic models define pண்ணினோம்.
4. `api/routes.py` la `POST /chat` endpoint create pண்ணி, idha `main.py` la `include_router()` mூலமா connect pண்ணினோம்.
5. Ollama server running-nு (`ollama list`) confirm pண்ணி, FastAPI server run pண்ணினோம்.
6. Swagger UI (`/docs`) mூலமா `POST /chat` test pண்ணி — request `{"message": "Hi, who are you?"}` anுப்பி, **200 OK** response `{"reply": "Hello! I'm an artificial intelligence model known as Llama..."}` verify pண்ணினோம்.

**Result:** Namma "chef" (LLM) ippo kitchen la ready, order (`/chat` request) kொடுத்தா dish (response) tharraார். Ippo Phase 3 la idha **WebSocket streaming** ku maатrанум — token-by-token live response, multi-device access.

---

## 2. Full Folder Structure (Phase 2 end state — new additions marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── utils\
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── helpers.py
│   ├── llm\                        ← NEW (Phase 2)
│   │   ├── __init__.py
│   │   ├── ollama_client.py        ← NEW
│   │   └── inference.py            ← NEW
│   └── api\
│       ├── __init__.py
│       ├── main.py                 ← UPDATED (router included)
│       ├── routes.py                ← UPDATED (/chat endpoint added)
│       └── schemas.py               ← UPDATED (ChatRequest/ChatResponse added)
├── venv\                          (excluded from git)
├── requirements.txt                ← UPDATED (ollama added)
├── setup.py
├── pyproject.toml
├── .env                           (excluded from git)
├── .gitignore
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Confirm Ollama Model Available
```
ollama list
```
(Confirms `llama3.2` is pulled and available before building the connection layer.)

### Step 2 — Create `llm/` Package
```
mkdir personal_ai_assistant\llm
type nul > personal_ai_assistant\llm\__init__.py
type nul > personal_ai_assistant\llm\ollama_client.py
type nul > personal_ai_assistant\llm\inference.py
```

### Step 3 — Install Ollama Python SDK
```
pip install -r requirements.txt --prefer-binary
```

### Step 4 — Verify Every File Before Running
```
python -m py_compile personal_ai_assistant\llm\ollama_client.py
python -m py_compile personal_ai_assistant\llm\inference.py
python -m py_compile personal_ai_assistant\api\schemas.py
python -m py_compile personal_ai_assistant\api\routes.py
python -m py_compile personal_ai_assistant\api\main.py
```

### Step 5 — Run Server (from outer folder `personal_ai_assistant_project`)
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6 — Test `/chat` Endpoint

**Option A — Swagger UI:**
Navigate to `http://localhost:8000/docs` → `POST /chat` → Try it out → body `{"message": "Hi, who are you?"}` → Execute

**Option B — curl:**
```
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Hi, who are you?\"}"
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
```

---

### `personal_ai_assistant\llm\__init__.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\llm\__init__.py`
```python
"""LLM Engine component — handles all Ollama model communication and inference."""
```

---

### `personal_ai_assistant\llm\ollama_client.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\llm\ollama_client.py`

**Purpose:** Single point of contact for talking to Ollama — wraps the Ollama Python SDK so no other file needs to know connection details directly.

```python
import ollama
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Wrapper around the Ollama client — single point of contact for the LLM engine."""

    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.model = settings.ollama_model

    def chat(self, message: str) -> str:
        """Send a single user message to the model and return the plain text reply."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": message}],
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise


ollama_client = OllamaClient()
```

---

### `personal_ai_assistant\llm\inference.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\llm\inference.py`

**Purpose:** Business logic layer between the API and the raw Ollama client. Future phases (Memory, RAG, Agents) extend this function without touching the API layer.

```python
from personal_ai_assistant.llm.ollama_client import ollama_client
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def generate_response(user_message: str) -> str:
    """Core inference function — takes user input, returns LLM output.

    Future phases (Memory, RAG, Agents) will extend this function
    without changing the API layer.
    """
    logger.info(f"Generating response for: {user_message[:50]}...")
    reply = ollama_client.chat(user_message)
    logger.info("Response generated successfully")
    return reply
```

---

### `personal_ai_assistant\api\schemas.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\schemas.py`

**Purpose:** Defines the exact shape of data going in/out of the API — FastAPI validates requests/responses against these automatically.

```python
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
```

---

### `personal_ai_assistant\api\routes.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\routes.py`

**Purpose:** Defines the `/chat` endpoint — connects incoming HTTP requests to the inference logic.

```python
from fastapi import APIRouter, HTTPException
from personal_ai_assistant.api.schemas import ChatRequest, ChatResponse
from personal_ai_assistant.llm.inference import generate_response
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        reply = generate_response(request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="LLM failed to generate a response")
```

---

### `personal_ai_assistant\api\main.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\main.py`

**Purpose:** FastAPI app entry point — now includes the `/chat` router alongside `/` and `/health`.

```python
from fastapi import FastAPI
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger
from personal_ai_assistant.api.routes import router

logger = get_logger(__name__)

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.get("/")
def root():
    logger.info("Root endpoint hit")
    return {
        "message": "Personal AI Assistant is running!",
        "app_name": settings.app_name,
        "configured_model": settings.ollama_model,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

---

## 5. Errors Faced & How We Solved Them

Phase 2 la major error varala — clean integration. Aana testing process la oru **confusion point** vandhுtchு, adha idhu la record pண்றோம்:

### Note: Partial log output during testing (not an actual error)

**What happened:** Testing pண்ணும்போது, first screenshot la server log `"Generating response for: Hi, who are you?..."` mattum kaाtitchu — response complete aachா, request hang aagi irukkaா nு clear ah theriyala.

**Karanam:** LLM inference — first time call pண்ணும்போது **model load pண்ண konjam time edukkum** (cold start). Adhан் log-um response-um oரே nேரத்la screenshot la kaाnбatha maadhiri irundhுtchு.

**Analogy:** Chef-kku first order kொடுத்தா, kitchen equipment warm-up aaga konjam time pidikkum. Rendாவது order fast ah varும். Idhு error illa — normal LLM behavior.

**Resolution:** Konjam wait pண்ணி, Swagger UI la "Response body" section check pண்ணினோம் — **200 OK** matrum full reply text confirmed வந்திருந்தது. No fix needed, just patience/wait for the model response.

**Status:** ✅ Not an error — confirmed working as expected.

---

## 6. Verified Test Results (Screenshot Confirmed)

**Request:**
```
POST http://localhost:8000/chat
Content-Type: application/json

{"message": "Hi, who are you?"}
```

**Response:**
```
Status: 200 OK
Content-Type: application/json
Content-Length: 337

{
  "reply": "Hello! I'm an artificial intelligence model known as Llama. Llama stands for \"Large Language Model Meta A.I.\" I was created to assist and communicate with users like you through text-based conversations. I can provide information, answer questions, and even generate text on a wide range of topics. How can I help you today?"
}
```

**Equivalent curl command (from Swagger UI):**
```
curl -X 'POST' \
  'http://localhost:8000/chat' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hi, who are you?"}'
```

---

## 7. Important Notes for Future Reference

- ⚠️ First LLM call after server start can take a few seconds longer (model cold start/load into memory) — this is normal, not an error.
- `inference.py` is the designated extension point — Memory (Phase 4), RAG (Phase 5), and Agents (Phase 6/7) will hook into `generate_response()` here, not into `routes.py` directly.
- `ollama_client.py` uses `settings.ollama_base_url` and `settings.ollama_model` from `config.py` (Phase 1) — model can be swapped centrally without touching this file.
- Current `/chat` endpoint is **synchronous** (waits for full response before replying) — Phase 3 will convert this to **streaming** over WebSocket for real-time, token-by-token output.
- Empty message validation (`400 Bad Request`) and LLM failure handling (`500 Internal Server Error`) are both already in place in `routes.py`.
- Ollama server must be running independently (`ollama serve` runs automatically in background after install) — always verify with `ollama list` before starting the FastAPI server.

---

## 8. Next Phase

**Phase 3: WebSocket Streaming** — convert the current request/response `/chat` endpoint into a WebSocket connection for real-time, token-by-token streaming, and enable simultaneous connections from laptop + mobile + tablet.

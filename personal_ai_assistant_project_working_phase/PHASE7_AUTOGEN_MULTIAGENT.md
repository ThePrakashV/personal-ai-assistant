# Phase 7: AutoGen Multi-Agent Layer (Specialized Agents Collaborating)

## Status: ✅ Complete
**Date:** 27-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 6 la namma **single agent** (calculator + datetime tools) build pண்ணினோம். Phase 7 la **multiple specialized agents** oருவரோடு oருவர் collaborate pண்ணும் system build pண்ணினோம் — AutoGen framework use pண்ணி:

1. `requirements.txt` la `autogen-agentchat`, `autogen-ext[ollama]`, matрும் (fix-ku apparam) `openai` add pண்ணினோம்.
2. Ollama-oda **built-in OpenAI-compatible endpoint** (`http://localhost:11434/v1`) confirm pண்ணினோம் — AutoGen-a "OpenAI server"-nு fool pண்ணி, actual ah local Ollama-கே connect aagும்படி setup pண்ணினோம்.
3. `utils/config.py` la AutoGen settings add pண்ணினோம் (OpenAI-compat URL, max turns safety limit).
4. `agents/autogen_agent.py` create pண்ணி, **மூன்று specialized agents** define pண்ணினோம் — Researcher (science/concepts/explanation), Coder (programming), General (greetings/coordination) — matрும் `SelectorGroupChat` (smart manager) mூலமா இணைத்தோம்.
5. Puthுsa **`/multiagent/chat`** endpoint add pண்ணினோம் (async, existing endpoints touch pண்ணாம).
6. **Rendு dependency-related errors** debug pண்ணி fix pண்ணினோம் (`openai` module missing, oru duplicate-command typo).
7. **Wrong agent routing issue** kண்டுபிடித்து fix pண்ணினோம் — initial ah "explain photosynthesis" question **Coder agent** kitta pогிducho (wrong), **explicit selector_prompt** add pண்ணின apparam, correct ah **Researcher agent**-kku route aachு.
8. **Three test scenarios** confirm pண்ணினோம் — code question → Coder, research question → Researcher, simple greeting → General — ellame correct agent-oda participate aachு.

**Result:** Namma AI Assistant ippo **oru "office team"** maadhiri — user-oda question-a paатthu, correct specialist agent-a automatic ah select pண்ணி, andha agent-oda focused response tharும். Single-agent (Phase 6) approach-a vida, ovvoru domain-லேயும் **better-focused** answers tharும் structure ready aagிyachू.

---

## 2. Full Folder Structure (Phase 7 end state — new/updated marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── utils\
│   │   ├── __init__.py
│   │   ├── config.py               ← UPDATED (AutoGen settings added)
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
│   │   └── memory_manager.py
│   ├── rag\
│   │   ├── __init__.py
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   └── retriever.py
│   ├── agents\
│   │   ├── __init__.py
│   │   ├── langchain_agent.py      (Phase 6)
│   │   ├── langgraph_workflow.py   (Phase 6)
│   │   └── autogen_agent.py        ← NEW (Phase 7)
│   └── api\
│       ├── __init__.py
│       ├── main.py
│       ├── routes.py                ← UPDATED (/multiagent/chat added)
│       ├── schemas.py               ← UPDATED (MultiAgentRequest/Response added)
│       └── websocket.py
├── data\
│   ├── documents\
│   │   └── company_policy.txt
│   ├── faiss_memory.index
│   ├── faiss_metadata.pkl
│   ├── rag_index.index
│   └── rag_metadata.pkl
├── venv\                          (excluded from git)
├── requirements.txt                ← UPDATED (autogen-agentchat, autogen-ext[ollama], openai added)
├── test_client.html
├── setup.py
├── pyproject.toml
├── .env                           (excluded from git)
├── .gitignore
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Update Dependencies
```
pip install -r requirements.txt --prefer-binary
```

### Step 2 — Verify Ollama's OpenAI-Compatible Endpoint
```
curl http://localhost:11434/v1/models
```

### Step 3 — Verify Every File Before Running
```
python -m py_compile personal_ai_assistant\utils\config.py
python -m py_compile personal_ai_assistant\agents\autogen_agent.py
python -m py_compile personal_ai_assistant\api\schemas.py
python -m py_compile personal_ai_assistant\api\routes.py
```

### Step 4 — Run Server (first attempt — hit missing `openai` module error, see Section 5)
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5 — Fix: Install Missing `openai` Package
```
pip install openai --prefer-binary
```

### Step 6 — Re-run Server
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7 — Test via curl (separate second CMD window)
```
curl -X POST http://localhost:8000/multiagent/chat -H "Content-Type: application/json" -d "{\"message\": \"Write a Python function to check if a number is prime\"}"

curl -X POST http://localhost:8000/multiagent/chat -H "Content-Type: application/json" -d "{\"message\": \"Explain how photosynthesis works\"}"

curl -X POST http://localhost:8000/multiagent/chat -H "Content-Type: application/json" -d "{\"message\": \"Hi, how are you?\"}"
```

### Step 8 — Fix: Add Explicit Selector Prompt (after wrong-agent-routing observed on photosynthesis test)
(Full replace of `autogen_agent.py` — see Section 4 for final code)

### Step 9 — Re-verify and Re-test
```
python -m py_compile personal_ai_assistant\agents\autogen_agent.py
```
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```
```
curl -X POST http://localhost:8000/multiagent/chat -H "Content-Type: application/json" -d "{\"message\": \"Explain how photosynthesis works\"}"
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
langchain
langchain-core
langchain-ollama
langgraph
autogen-agentchat
autogen-ext[ollama]
openai
```

---

### `personal_ai_assistant\utils\config.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\utils\config.py`

**Purpose:** Added AutoGen-specific settings — the OpenAI-compatible URL Ollama exposes, and a safety limit on how many messages the multi-agent team can exchange.

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

    # Agent (LangChain / LangGraph)
    agent_max_tool_loops: int = 3

    # Multi-Agent (AutoGen)
    autogen_openai_compat_url: str = "http://localhost:11434/v1"
    autogen_max_turns: int = 6

    class Config:
        env_file = ".env"


settings = Settings()
```

---

### `personal_ai_assistant\agents\autogen_agent.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\agents\autogen_agent.py`

**Purpose:** Defines three specialized agents (Researcher, Coder, General) and a `SelectorGroupChat` "team" that routes each user message to the most appropriate agent. Includes an explicit `selector_prompt` (added after debugging a wrong-routing issue — see Section 5) to make the routing decision reliable.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def _make_model_client() -> OpenAIChatCompletionClient:
    """Points AutoGen at our local Ollama server via its OpenAI-compatible endpoint."""
    return OpenAIChatCompletionClient(
        model=settings.ollama_model,
        base_url=settings.autogen_openai_compat_url,
        api_key="ollama",
        model_info={
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": "unknown",
        },
    )


# --- Specialized Agents ---

researcher_agent = AssistantAgent(
    name="Researcher",
    model_client=_make_model_client(),
    system_message=(
        "You are a Research Agent. You explain concepts, facts, science, history, and "
        "provide analysis clearly and concisely. You do NOT write code — if the request "
        "needs code, say so and let the Coder agent handle it. When you have fully "
        "answered the user's question, end your message with TERMINATE."
    ),
)

coder_agent = AssistantAgent(
    name="Coder",
    model_client=_make_model_client(),
    system_message=(
        "You are a Coding Agent. You ONLY write code, debug code, or explain programming "
        "concepts. You do NOT handle general research/science/explanation topics unrelated "
        "to code — defer those to the Researcher agent. When you have fully answered the "
        "user's question, end your message with TERMINATE."
    ),
)

general_agent = AssistantAgent(
    name="General",
    model_client=_make_model_client(),
    system_message=(
        "You are a General Assistant and coordinator. You handle simple everyday "
        "greetings and small talk directly. For anything requiring deep research, "
        "science, or explanation, defer to the Researcher agent. For anything requiring "
        "code, defer to the Coder agent. When the conversation has fully answered the "
        "user's question, end your message with TERMINATE."
    ),
)

ALL_AGENTS = [general_agent, researcher_agent, coder_agent]

# --- Selector instructions (explicit routing guidance) ---

_SELECTOR_PROMPT = """You are selecting the next agent to speak in a conversation.

Available agents:
- General: handles simple greetings and small talk only (e.g. "hi", "how are you").
- Researcher: handles science, history, concepts, facts, and any explanation/analysis
  question that does NOT involve writing code (e.g. "explain photosynthesis", "who is Einstein").
- Coder: handles ONLY requests to write, debug, or explain code/programming
  (e.g. "write a Python function", "fix this bug").

Conversation so far:
{history}

Based on the user's most recent message, select the SINGLE most appropriate agent from
{participants} to respond next. Respond with ONLY the agent name, nothing else.
"""

# --- Team (Group Chat) ---

_termination = MaxMessageTermination(settings.autogen_max_turns) | TextMentionTermination("TERMINATE")

team = SelectorGroupChat(
    participants=ALL_AGENTS,
    model_client=_make_model_client(),
    termination_condition=_termination,
    selector_prompt=_SELECTOR_PROMPT,
)


async def run_multiagent(user_message: str) -> str:
    """Run the multi-agent team on a single user message and return the final reply text."""
    logger.info(f"Running multi-agent team for: {user_message[:50]}...")

    result = await team.run(task=user_message)

    for msg in result.messages:
        source = getattr(msg, "source", "unknown")
        content_preview = (getattr(msg, "content", "") or "")[:60]
        logger.info(f"  [{source}]: {content_preview}...")

    final_text = ""
    for msg in reversed(result.messages):
        content = getattr(msg, "content", "") or ""
        cleaned = content.replace("TERMINATE", "").strip()
        if cleaned:
            final_text = cleaned
            break

    logger.info("Multi-agent run completed")
    return final_text or "No response generated."
```

---

### `personal_ai_assistant\api\schemas.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\schemas.py`

**Purpose:** Added `MultiAgentRequest`/`MultiAgentResponse` for the new `/multiagent/chat` endpoint.

```python
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class IngestResponse(BaseModel):
    filename: str
    chunks_added: int


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    reply: str


class MultiAgentRequest(BaseModel):
    message: str


class MultiAgentResponse(BaseModel):
    reply: str
```

---

### `personal_ai_assistant\api\routes.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\routes.py`

**Purpose:** Added `POST /multiagent/chat` — an async endpoint that runs the AutoGen multi-agent team and returns the final response.

```python
import os
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File

from personal_ai_assistant.api.schemas import (
    ChatRequest, ChatResponse, IngestResponse,
    AgentRequest, AgentResponse,
    MultiAgentRequest, MultiAgentResponse,
)
from personal_ai_assistant.llm.inference import generate_response
from personal_ai_assistant.rag.retriever import rag_retriever
from personal_ai_assistant.agents.langgraph_workflow import run_agent
from personal_ai_assistant.agents.autogen_agent import run_multiagent
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


@router.post("/agent/chat", response_model=AgentResponse)
def agent_chat(request: AgentRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        reply = run_agent(request.message)
        return AgentResponse(reply=reply)
    except Exception as e:
        logger.error(f"Agent chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Agent failed to generate a response")


@router.post("/multiagent/chat", response_model=MultiAgentResponse)
async def multiagent_chat(request: MultiAgentRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        reply = await run_multiagent(request.message)
        return MultiAgentResponse(reply=reply)
    except Exception as e:
        logger.error(f"Multi-agent chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Multi-agent team failed to generate a response")
```

---

## 5. Errors Faced & How We Solved Them

### Error 1: `ModuleNotFoundError: No module named 'openai'`

**Exact error seen:**
```
File "...autogen_ext\models\openai\_message_transform.py", line 151, in <module>
    from openai.types.chat import (
ModuleNotFoundError: No module named 'openai'
```

**Karanam (Root Cause):** `OpenAIChatCompletionClient` (used to point AutoGen at Ollama's OpenAI-compatible endpoint) internally depends on the `openai` Python package for its type definitions/schemas — even though we're not actually calling OpenAI's servers. `autogen-ext[ollama]` alone does not pull in `openai` as a dependency; it needed to be installed separately.

**Analogy:** "OpenAI-style adapter plug" (OpenAIChatCompletionClient) vachi Ollama-a connect pண்ண try pண்ணினோம், aana andha adapter-oda உள்ளே irukும் wiring kit (openai package) install aagவில்லை.

**Fix:**
```
pip install openai --prefer-binary
```
Added to `requirements.txt` as well.

**Status:** ✅ Resolved — confirmed by successful `Application startup complete` on the next server run.

---

### Error 2: `no such option: --prefer-binarypip` (typo/duplicate command)

**Exact error seen:**
```
pip install openai --prefer-binarypip install openai --prefer-binary
...
no such option: --prefer-binarypip
```

**Karanam (Root Cause):** The command got accidentally duplicated/concatenated while typing or pasting into CMD, producing an invalid combined option (`--prefer-binarypip`) that pip couldn't recognize.

**Status:** ✅ Not a code issue — retyping the exact single command (`pip install openai --prefer-binary`) resolved it immediately.

---

### Error 3: Wrong agent answering — Coder agent responded to a science question

**What happened:** When asked "Explain how photosynthesis works", the response came from what was clearly the **Coder** agent, not the Researcher:
> "I'm not a scientist or a general research resource. This text provides a detailed explanation of photosynthesis. If you have any specific code-related questions..."

Meanwhile, "Write a Python function to check if a number is prime" and "Hi, how are you?" were correctly routed to Coder and General respectively.

**Karanam (Root Cause):** `SelectorGroupChat` uses an LLM (in this case, the same small `llama3.2` model) to decide which agent should speak next. Without **explicit, detailed routing instructions**, a small model can inconsistently judge which agent's scope a given question falls into — especially for topics that don't obviously scream "science" or "code" in their exact wording.

**Analogy:** Namma "office manager" (selector) kitta "yaாருக்கு idha kொடுக்கணும்" nு clear ah training kொடுக்காமல் விட்டோம் — adhால் சில வேளைகளில் wrong desk-கு file கொடுத்துடுத்து.

**Fix:** Added an explicit `_SELECTOR_PROMPT` to `autogen_agent.py`, clearly listing each agent's exact scope with examples, and passed it to `SelectorGroupChat` via the `selector_prompt` parameter. Also added per-message logging (`logger.info(f"  [{source}]: ...")`) in `run_multiagent()` so which agent responded can be verified from server logs going forward.

**Status:** ✅ Resolved — after the fix, re-testing the exact same photosynthesis question produced a detailed, scientifically accurate, code-free explanation (light-dependent reactions, Calvin cycle, overall chemical equation), consistent with the Researcher agent's system prompt and clearly distinct from the Coder agent's earlier response style.

---

## 6. Verified Test Results

| Test | Query | Expected Agent | Result |
|---|---|---|---|
| Code question | `Write a Python function to check if a number is prime` | Coder | ✅ Correct — full working Python code with docstring and example usage |
| Research question (before fix) | `Explain how photosynthesis works` | Researcher | ❌ Wrong — Coder agent responded instead, deferring the question |
| Research question (after fix) | `Explain how photosynthesis works` | Researcher | ✅ Correct — detailed, scientific explanation (light-dependent reactions, Calvin cycle, chemical equation), no code-focused framing |
| Simple greeting | `Hi, how are you?` | General | ✅ Correct — friendly response explaining its role and when it defers to specialists |

**Confirmed:** After adding the explicit `selector_prompt`, all three test categories routed to the correct specialized agent.

---

## 7. Important Notes for Future Reference

- ⚠️ **`OpenAIChatCompletionClient` requires the `openai` package installed**, even when only talking to a local Ollama server via its OpenAI-compatible endpoint (`http://localhost:11434/v1`) — this is a hidden dependency not obvious from `autogen-ext[ollama]` alone.
- ⚠️ **A small local model (like `llama3.2`) needs an explicit, detailed `selector_prompt`** to route between agents reliably — don't rely on the default selector behavior alone when agent scopes could plausibly overlap.
- Multi-agent responses take noticeably longer than single-agent (Phase 6) responses — since multiple agents (and the selector itself) may each make a separate LLM call per turn. This is expected and not a performance bug.
- `run_multiagent()` now logs every message with its source agent (`[Researcher]: ...`, `[Coder]: ...`, etc.) — useful for verifying correct routing during any future debugging, directly from server terminal logs.
- `/multiagent/chat` is currently **independent** of memory (Phase 4), RAG (Phase 5), and the single-agent tools (Phase 6) — same as `/agent/chat`, this is intentional for now to keep each phase's functionality isolated and easy to verify. A future consolidation phase could combine memory + RAG + tools + multi-agent into one unified endpoint.
- `MaxMessageTermination(settings.autogen_max_turns)` (currently 6) prevents agents from talking indefinitely if `TERMINATE` is never produced — this safety limit should be revisited if more complex multi-turn agent collaboration is needed later.

---

## 8. Next Phase

**Phase 8: Voice Input/Output** — add Whisper-based speech-to-text (voice input) and text-to-speech (voice output), so the assistant can be used hands-free across devices, building on the conversational and agent capabilities established so far.

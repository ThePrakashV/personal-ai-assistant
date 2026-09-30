# Phase 6: LangChain/LangGraph Agent Workflow (Tool-Calling + Decision Routing)

## Status: ✅ Complete
**Date:** 27-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 5 vare namma assistant **conversation memory + document knowledge** vachirundhுchু, aana ella questions-kkum **LLM directly** answer pண்ணிyachu — math, real-time date/time maadhiri things-la LLM weak (hallucinate pண்ணும் illa "I don't have access" nू sollум்). Phase 6 la **Agent workflow** build pண்ணி, LLM-ku **tools** kொடுthோம்:

1. Puthusa `agents/` package create pண்ணினோம் — `langchain_agent.py` (tools + tool-bound model) matrும் `langgraph_workflow.py` (decision flowchart/graph).
2. `requirements.txt` la `langchain`, `langchain-core`, `langchain-ollama`, `langgraph` add pண்ணினோம்.
3. **Rendு tools** define pண்ணினோம்: `calculator` (safe `ast`-based arithmetic evaluation, `eval()` illa — security best practice) matrும் `get_current_datetime` (real system clock access).
4. **LangGraph StateGraph** build pண்ணினோம் — `agent` node (LLM decide pண்றுthு tool thேவைya nு) matrும் `tools` node (ToolNode, actual tool run pண்றுthு), rendையும் conditional edge மூலமா இணைத்து.
5. Puthுsa **`/agent/chat`** endpoint add pண்ணினோம் (existing `/chat` matrும் `/ws/chat` touch pண்ணாம — agent workflow tool-loop pண்றுதால், streaming-oda naturally fit aagாthு, adhான் separate endpoint).
6. **Three test scenarios** verify pண்ணினோம் — math (calculator tool), date/time (datetime tool), general knowledge (no tool, direct LLM answer) — ellame correct ah work aachு.
7. Journey-la **rendு confusion points** debug pண்ணினோம் — Swagger UI accidentally wrong endpoint (`/chat` illa `/agent/chat`) hit pண்ண, matrும் oru terminal paste mistake.

**Result:** Assistant ippo **"idhுku tool thேவையா illaya"** nு தானே decide pண்ணி, thேவைna calculator/clock use pண்ணி **accurate ah** answer pண்ணும், illainaாlும் LLM knowledge-a direct ah use pண்ணும். Confirmed: `347 * 89` → correct ah **30883** (LLM mental math wrong ah irundhা, tool correct ah fix pண்ணிyachు), real-time date/time → **actual current value**, general knowledge → **direct answer, no unnecessary tool call**.

---

## 2. Full Folder Structure (Phase 6 end state — new/updated marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── utils\
│   │   ├── __init__.py
│   │   ├── config.py               ← UPDATED (agent settings added)
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
│   ├── agents\                     ← NEW (Phase 6)
│   │   ├── __init__.py
│   │   ├── langchain_agent.py      ← NEW (tools + tool-bound model)
│   │   └── langgraph_workflow.py   ← NEW (decision graph)
│   └── api\
│       ├── __init__.py
│       ├── main.py
│       ├── routes.py                ← UPDATED (/agent/chat added)
│       ├── schemas.py               ← UPDATED (AgentRequest/AgentResponse added)
│       └── websocket.py
├── data\
│   ├── documents\
│   │   └── company_policy.txt
│   ├── faiss_memory.index
│   ├── faiss_metadata.pkl
│   ├── rag_index.index
│   └── rag_metadata.pkl
├── venv\                          (excluded from git)
├── requirements.txt                ← UPDATED (langchain, langgraph added)
├── test_client.html
├── setup.py
├── pyproject.toml
├── .env                           (excluded from git)
├── .gitignore
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Create `agents/` Package
```
mkdir personal_ai_assistant\agents
type nul > personal_ai_assistant\agents\__init__.py
type nul > personal_ai_assistant\agents\langchain_agent.py
type nul > personal_ai_assistant\agents\langgraph_workflow.py
```

### Step 2 — Update Dependencies
```
pip install -r requirements.txt --prefer-binary
```

### Step 3 — Verify Every File Before Running
```
python -m py_compile personal_ai_assistant\utils\config.py
python -m py_compile personal_ai_assistant\agents\langchain_agent.py
python -m py_compile personal_ai_assistant\agents\langgraph_workflow.py
python -m py_compile personal_ai_assistant\api\schemas.py
python -m py_compile personal_ai_assistant\api\routes.py
```

### Step 4 — Run Server (dedicated CMD window, kept open)
```
cd D:\project\personal_ai_assistant_project
venv\Scripts\activate
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5 — Verify Ollama Version (tool-calling support check)
```
ollama --version
```

### Step 6 — Test via curl (separate second CMD window)
```
curl -X POST http://localhost:8000/agent/chat -H "Content-Type: application/json" -d "{\"message\": \"What is 347 * 89?\"}"

curl -X POST http://localhost:8000/agent/chat -H "Content-Type: application/json" -d "{\"message\": \"What is today's date and time?\"}"

curl -X POST http://localhost:8000/agent/chat -H "Content-Type: application/json" -d "{\"message\": \"What is the capital of France?\"}"
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
```

---

### `personal_ai_assistant\utils\config.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\utils\config.py`

**Purpose:** Added `agent_max_tool_loops` — a safety limit to prevent the agent from getting stuck in an infinite tool-call loop.

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

    class Config:
        env_file = ".env"


settings = Settings()
```

---

### `personal_ai_assistant\agents\langchain_agent.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\agents\langchain_agent.py`

**Purpose:** Defines the two tools available to the agent (`calculator`, `get_current_datetime`) and binds them to the Ollama chat model so the LLM knows it can call them.

```python
import ast
import operator
from datetime import datetime

from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


# --- Tools ---

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval(node):
    """Safely evaluate a basic arithmetic expression (no eval() — avoids code execution risk)."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _SAFE_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression (e.g. '25 * 48', '(10 + 5) / 3'). Use this for any math question."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        logger.info(f"Calculator: {expression} = {result}")
        return str(result)
    except Exception as e:
        logger.error(f"Calculator failed for '{expression}': {e}")
        return f"Error: could not evaluate '{expression}'"


@tool
def get_current_datetime() -> str:
    """Return the current date and time. Use this whenever the user asks what the date or time is."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"get_current_datetime: {now}")
    return now


TOOLS = [calculator, get_current_datetime]

# --- Tool-bound model ---

_base_model = ChatOllama(base_url=settings.ollama_base_url, model=settings.ollama_model)
model_with_tools = _base_model.bind_tools(TOOLS)
```

**Security note:** `calculator` deliberately avoids Python's built-in `eval()` and instead parses the expression into an Abstract Syntax Tree (`ast`), evaluating only a fixed whitelist of safe arithmetic operators. This prevents arbitrary code execution even if a malicious expression string reached this function.

---

### `personal_ai_assistant\agents\langgraph_workflow.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\agents\langgraph_workflow.py`

**Purpose:** Builds the LangGraph decision flowchart — an `agent` node (LLM decides whether a tool is needed) and a `tools` node (runs the requested tool), looping back to the agent until a final answer is produced.

```python
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from personal_ai_assistant.agents.langchain_agent import model_with_tools, TOOLS
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def call_model(state: AgentState) -> dict:
    """Agent node — asks the LLM to respond, possibly requesting a tool call."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Decision node — if the last message requested a tool call, go run it; otherwise finish."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


# --- Build the graph ---

_workflow = StateGraph(AgentState)
_workflow.add_node("agent", call_model)
_workflow.add_node("tools", ToolNode(TOOLS))

_workflow.set_entry_point("agent")
_workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
_workflow.add_edge("tools", "agent")

agent_graph = _workflow.compile()


def run_agent(user_message: str) -> str:
    """Run the agent workflow for a single user message and return the final text reply."""
    logger.info(f"Running agent for: {user_message[:50]}...")

    result = agent_graph.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config={"recursion_limit": settings.agent_max_tool_loops * 2 + 2},
    )

    final_message = result["messages"][-1]
    logger.info("Agent run completed")
    return final_message.content
```

**Flowchart:**
```
[User message] → [agent node: LLM decides]
                        │
          ┌─────────────┴─────────────┐
     tool needed?                no tool needed
          │                             │
     [tools node runs]              [END — return answer]
          │
     back to [agent node] → LLM gives final answer using tool result
```

---

### `personal_ai_assistant\api\schemas.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\schemas.py`

**Purpose:** Added `AgentRequest`/`AgentResponse` for the new `/agent/chat` endpoint.

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
```

---

### `personal_ai_assistant\api\routes.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\routes.py`

**Purpose:** Added `POST /agent/chat` — a standalone endpoint that runs the LangGraph agent workflow (tool-calling enabled), kept separate from `/chat` and `/ws/chat` since the tool-call loop doesn't naturally fit real-time streaming.

```python
import os
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File

from personal_ai_assistant.api.schemas import (
    ChatRequest, ChatResponse, IngestResponse, AgentRequest, AgentResponse,
)
from personal_ai_assistant.llm.inference import generate_response
from personal_ai_assistant.rag.retriever import rag_retriever
from personal_ai_assistant.agents.langgraph_workflow import run_agent
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
```

**Note:** `/agent/chat` does not currently use conversation memory (Phase 4) or document retrieval (Phase 5) — it's a standalone endpoint focused purely on demonstrating tool-calling. Integrating agent + memory + RAG together can be considered in a future consolidation phase.

---

## 5. Errors Faced & How We Solved Them

### Error 1: Math answer was wrong and date/time answer showed the old "no real-time access" limitation

**What happened:** First test via Swagger UI gave `{"reply": "347 * 89 = 31053."}` (incorrect — actual answer is 30883) and `{"reply": "I don't have real-time access to the current date and time..."}` for the date/time question — both exactly like the pre-agent behavior from earlier phases.

**Karanam (Root Cause):** On closer inspection of the Swagger UI screenshots, the **Request URL was `http://localhost:8000/chat`**, not `/agent/chat`. The old Phase 2/4/5 `/chat` endpoint (which has no tools bound to it) was being tested by mistake — not the new agent endpoint. So this wasn't a bug in the agent code at all; the wrong endpoint was simply being called.

**Analogy:** Namma puthusa "tool-equipped chef" (agent endpoint) kitchen-ku add pண்ணினோம், aana order **pழைய chef-கிட்டே** (old `/chat` endpoint) pогிduchu — adhான் old (tool-less) results வந்திருச்சு.

**Fix:** Retested using `curl` directly against the exact correct URL:
```
curl -X POST http://localhost:8000/agent/chat -H "Content-Type: application/json" -d "{\"message\": \"What is 347 * 89?\"}"
```
This returned the correct, tool-verified answer: `{"reply":"The result of 347 * 89 is 30883."}`

**Status:** ✅ Resolved — confirmed to be a testing mistake (wrong endpoint), not a code defect. All three test cases subsequently passed correctly against `/agent/chat`.

---

### Error 2 (Minor — not a real error): Terminal paste mistake caused a "filename, directory name, or volume label syntax is incorrect" message

**What happened:** While testing the third case (capital of France), the CMD window showed:
```
D:\project\personal_ai_assistant_project>{"reply":"The current date is September 27, 2026, and the current time is 8:57 PM."}
The filename, directory name, or volume label syntax is incorrect.
```

**Karanam (Root Cause):** This happened because a previous response's JSON text was accidentally pasted directly into the CMD prompt (instead of a new `curl` command), and Windows CMD tried to interpret that JSON text as a command/filename, which failed.

**Status:** ✅ Not a code issue — purely a copy-paste mistake during manual testing. No fix needed; the next correctly-typed `curl` command worked fine immediately after.

---

## 6. Verified Test Results (Screenshots Confirmed)

| Test | Query | Expected Behavior | Result |
|---|---|---|---|
| Math (calculator tool) | `What is 347 * 89?` | Tool computes exact value, not LLM mental math | ✅ `{"reply":"The result of 347 * 89 is 30883."}` (correct — verified: 347×89=30883) |
| Date/time (datetime tool) | `What is today's date and time?` | Tool returns actual system clock value | ✅ `{"reply":"The current date is September 27, 2026, and the current time is 8:57 PM."}` |
| General knowledge (no tool) | `What is the capital of France?` | LLM answers directly, no tool call | ✅ `{"reply":"The capital of France is Paris."}` |

**Environment confirmed:** `ollama --version` → `ollama version is 0.34.4` (supports tool-calling required by `bind_tools()`).

---

## 7. Important Notes for Future Reference

- ⚠️ **Always double-check the Request URL when testing via Swagger UI** — the browser tab can retain an old expanded endpoint, making it easy to accidentally test the wrong route (this caused Error 1 above). Prefer `curl` with an explicit full URL for unambiguous testing.
- ⚠️ **When pasting into CMD, always paste a fresh command** — pasting a previous JSON *response* by mistake will be misinterpreted by CMD as a command/filename (Error 2).
- `/agent/chat` is currently **independent** of memory (Phase 4) and RAG (Phase 5) — it has no session_id, no conversation history, and no document context. This is intentional for Phase 6 to keep tool-calling logic isolated and easy to verify; combining them is a candidate for a future integration phase.
- `calculator` tool uses safe `ast`-based evaluation, never Python's `eval()` — this should remain the pattern for any future tools that evaluate user-supplied expressions.
- `agent_max_tool_loops` (in `config.py`) guards against the agent getting stuck calling tools repeatedly without producing a final answer — currently set to 3, can be tuned later if more complex multi-tool reasoning is needed.
- Adding a new tool in the future is straightforward: define a new `@tool`-decorated function in `langchain_agent.py`, add it to the `TOOLS` list — no changes needed in `langgraph_workflow.py` itself.

---

## 8. Next Phase

**Phase 7: AutoGen Multi-Agent Layer** — introduce specialized agents (e.g. a research agent, a code agent, a general-purpose agent) that can collaborate on more complex requests, building on top of the single-agent tool-calling foundation established in this phase.

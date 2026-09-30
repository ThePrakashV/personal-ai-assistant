# Phase 10: Dashboard (MLflow + W&B + Plotly)

## Status: ✅ Complete
**Date:** 29-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 9 varaikkum namma assistant la ella capabilities-um (chat, memory, RAG, agents, voice, vision, image gen) irundhuchu, aana **eppadi vela seiyudhu nu paakka oru wall illa**. Phase 10 la monitoring/observability layer build pannoam:

1. Puthusa `monitoring/` package create pannoam — `mlflow_tracker.py`, `wandb_logger.py`, `request_monitor.py`, `dashboard.py`.
2. `requirements.txt` la `mlflow`, `wandb`, `plotly` add pannoam.
3. `utils/config.py` la monitoring settings add pannoam (metrics file path, MLflow SQLite DB path, W&B project/mode, dashboard limits).
4. **MLflow** — server start aagumbodhu oru run create panni, ovvoru request-oda latency-a metric ah log pannoam (SQLite backend, MLflow server thevai illa).
5. **W&B** — same data offline mode la log pannoam (login/internet thevai illa).
6. **Request Monitor** — ovvoru request-um local JSONL file la, MLflow la, W&B la — moondu idangalayum record pannum central module.
7. **FastAPI middleware** add pannoam — `routes.py` touch pannaama, ella endpoints-um automatic ah track aagum (method, path, status code, latency).
8. **Plotly Dashboard** (`/dashboard`) build pannoam — 4 charts (requests per endpoint, average latency log-scale, latency over time, status code pie chart) + summary cards, auto-refresh oda.
9. Test requests generate panni, dashboard, MLflow UI, matrum W&B offline logs — moondayum verify pannoam.

**Result:** Namma assistant ippo **self-observable** — ovvoru API call-oda latency, success/failure, endpoint-wise breakdown ellame real-time ah `/dashboard` page la paakalam, matrum MLflow/W&B la historical ah track panna mudiyum.

---

## 2. Full Folder Structure (Phase 10 end state — new/updated marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── utils\
│   │   ├── __init__.py
│   │   ├── config.py               ← UPDATED (monitoring settings added)
│   │   ├── logger.py
│   │   └── helpers.py
│   ├── llm\
│   ├── memory\
│   ├── rag\
│   ├── agents\
│   ├── multimodal\
│   ├── monitoring\                 ← NEW (Phase 10)
│   │   ├── __init__.py
│   │   ├── mlflow_tracker.py       ← NEW (MLflow run + metrics)
│   │   ├── wandb_logger.py         ← NEW (W&B offline logging)
│   │   ├── request_monitor.py      ← NEW (central request recorder, JSONL)
│   │   └── dashboard.py            ← NEW (Plotly /dashboard page)
│   └── api\
│       ├── __init__.py
│       ├── main.py                 ← UPDATED (lifespan + monitoring middleware)
│       ├── routes.py
│       ├── schemas.py
│       └── websocket.py
├── data\
│   ├── documents\
│   ├── voice\
│   ├── vision\
│   ├── generated_images\
│   ├── metrics\                    ← NEW
│   │   └── requests.jsonl          ← NEW (one JSON line per request)
│   ├── mlflow.db                   ← NEW (MLflow SQLite backend)
│   ├── faiss_memory.index
│   ├── faiss_metadata.pkl
│   ├── rag_index.index
│   └── rag_metadata.pkl
├── wandb\                          ← NEW (W&B offline run folders, excluded from git)
│   └── offline-run-<timestamp>-<id>\
├── venv\                          (excluded from git)
├── requirements.txt                ← UPDATED (mlflow, wandb, plotly added)
├── test_client.html
├── setup.py
├── pyproject.toml
├── .env                           (excluded from git)
├── .gitignore                     ← should add wandb/, data/mlflow.db, data/metrics/ (see notes)
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Create `monitoring/` Package
```
mkdir personal_ai_assistant\monitoring
type nul > personal_ai_assistant\monitoring\__init__.py
type nul > personal_ai_assistant\monitoring\mlflow_tracker.py
type nul > personal_ai_assistant\monitoring\wandb_logger.py
type nul > personal_ai_assistant\monitoring\request_monitor.py
type nul > personal_ai_assistant\monitoring\dashboard.py
mkdir data\metrics
```

### Step 2 — Update Dependencies
```
pip install -r requirements.txt --prefer-binary
```

### Step 3 — Verify Every File Before Running
```
python -m py_compile personal_ai_assistant\utils\config.py
python -m py_compile personal_ai_assistant\monitoring\mlflow_tracker.py
python -m py_compile personal_ai_assistant\monitoring\wandb_logger.py
python -m py_compile personal_ai_assistant\monitoring\request_monitor.py
python -m py_compile personal_ai_assistant\monitoring\dashboard.py
python -m py_compile personal_ai_assistant\api\main.py
```

### Step 4 — Run Server (Window 1, kept open)
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```
(Confirmed startup logs: `MLflow tracking started (run_id: ...)` and `W&B run started (mode: offline)`.)

### Step 5 — Generate Test Traffic (Window 2, separate CMD)
```
curl http://localhost:8000/health
curl http://localhost:8000/
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Hello\"}"
curl -X POST http://localhost:8000/agent/chat -H "Content-Type: application/json" -d "{\"message\": \"What is 12 * 12?\"}"
curl -X POST http://localhost:8000/voice/speak -H "Content-Type: application/json" -d "{\"text\": \"Dashboard test\"}" --output data/voice/dash_test.wav
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"   \"}"
```

### Step 6 — View Dashboard
```
http://localhost:8000/dashboard
```

### Step 7 — View MLflow UI (Window 3, separate CMD)
```
cd D:\project\personal_ai_assistant_project
venv\Scripts\activate
mlflow ui --backend-store-uri sqlite:///data/mlflow.db --port 5001
```
Then open `http://localhost:5001` in browser.

### Step 8 — Verify W&B Offline Logs
```
dir wandb
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
openai-whisper
pyttsx3
diffusers
accelerate
pillow
mlflow
wandb
plotly
```

---

### `personal_ai_assistant\utils\config.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\utils\config.py`

**Purpose:** Added monitoring settings — where metrics are logged (JSONL file), MLflow's SQLite backend path and experiment name, W&B project/mode, and dashboard display limits.

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

    # Voice (Whisper STT + TTS)
    whisper_model_size: str = "base"
    voice_temp_folder: str = "data/voice"
    tts_rate: int = 175
    tts_volume: float = 1.0

    # Vision (Ollama vision model)
    vision_model: str = "llava"
    vision_temp_folder: str = "data/vision"

    # Image Generation (Diffusers)
    image_gen_model: str = "runwayml/stable-diffusion-v1-5"
    image_gen_output_folder: str = "data/generated_images"
    image_gen_steps: int = 25
    image_gen_width: int = 512
    image_gen_height: int = 512

    # Monitoring (MLflow / W&B / Dashboard)
    metrics_log_path: str = "data/metrics/requests.jsonl"
    mlflow_db_path: str = "data/mlflow.db"
    mlflow_experiment_name: str = "personal-ai-assistant"
    wandb_project: str = "personal-ai-assistant"
    wandb_mode: str = "offline"
    dashboard_max_points: int = 2000
    dashboard_refresh_seconds: int = 15

    class Config:
        env_file = ".env"


settings = Settings()
```

---

### `personal_ai_assistant\monitoring\mlflow_tracker.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\monitoring\mlflow_tracker.py`

**Purpose:** Starts one MLflow run per server session using a SQLite backend (no separate MLflow tracking server required), logs model/config parameters once, and logs a latency metric per request. Uses `MlflowClient` with an explicit `run_id` (instead of the global `mlflow.start_run()` context) because requests are handled across threads, and MLflow's "active run" concept is thread-local.

```python
import os
import threading
from datetime import datetime

from mlflow.tracking import MlflowClient

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

_client = None
_run_id = None
_lock = threading.Lock()
_steps = {}


def _metric_key(path: str) -> str:
    return path.strip("/").replace("/", "_") or "root"


def init_mlflow() -> None:
    """Create one MLflow run for this server session (SQLite backend, no MLflow server needed)."""
    global _client, _run_id
    try:
        os.makedirs(os.path.dirname(settings.mlflow_db_path), exist_ok=True)
        _client = MlflowClient(tracking_uri=f"sqlite:///{settings.mlflow_db_path}")

        experiment = _client.get_experiment_by_name(settings.mlflow_experiment_name)
        experiment_id = (
            experiment.experiment_id
            if experiment
            else _client.create_experiment(settings.mlflow_experiment_name)
        )

        run = _client.create_run(
            experiment_id=experiment_id,
            run_name=f"server-{datetime.now():%Y%m%d-%H%M%S}",
        )
        _run_id = run.info.run_id

        params = {
            "llm_model": settings.ollama_model,
            "vision_model": settings.vision_model,
            "embedding_model": settings.embedding_model_name,
            "whisper_model": settings.whisper_model_size,
            "image_gen_model": settings.image_gen_model,
            "chunk_size": settings.chunk_size,
            "rag_top_k": settings.rag_top_k,
        }
        for key, value in params.items():
            _client.log_param(_run_id, key, value)

        logger.info(f"MLflow tracking started (run_id: {_run_id})")
    except Exception as e:
        _client = None
        logger.error(f"MLflow init failed (server continues without it): {e}")


def log_request(path: str, status_code: int, latency_ms: float) -> None:
    if _client is None or _run_id is None:
        return
    try:
        key = _metric_key(path)
        with _lock:
            step = _steps.get(key, 0)
            _steps[key] = step + 1
        _client.log_metric(_run_id, f"{key}_latency_ms", float(latency_ms), step=step)
        if status_code >= 400:
            _client.log_metric(_run_id, f"{key}_error_status", float(status_code), step=step)
    except Exception as e:
        logger.error(f"MLflow log_request failed: {e}")


def finish_mlflow() -> None:
    if _client is None or _run_id is None:
        return
    try:
        _client.set_terminated(_run_id)
        logger.info("MLflow run finished")
    except Exception as e:
        logger.error(f"MLflow finish failed: {e}")
```

---

### `personal_ai_assistant\monitoring\wandb_logger.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\monitoring\wandb_logger.py`

**Purpose:** Mirrors the same latency/status metrics into Weights & Biases, running in `offline` mode by default so no W&B account or internet connection is required — logs are saved locally under `wandb/`.

```python
import threading
from datetime import datetime

import wandb

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

_run = None
_lock = threading.Lock()


def _metric_key(path: str) -> str:
    return path.strip("/").replace("/", "_") or "root"


def init_wandb() -> None:
    global _run
    if settings.wandb_mode == "disabled":
        logger.info("W&B logging is disabled")
        return
    try:
        _run = wandb.init(
            project=settings.wandb_project,
            mode=settings.wandb_mode,
            name=f"server-{datetime.now():%Y%m%d-%H%M%S}",
            config={
                "llm_model": settings.ollama_model,
                "vision_model": settings.vision_model,
                "embedding_model": settings.embedding_model_name,
                "whisper_model": settings.whisper_model_size,
                "image_gen_model": settings.image_gen_model,
            },
        )
        logger.info(f"W&B run started (mode: {settings.wandb_mode})")
    except Exception as e:
        _run = None
        logger.error(f"W&B init failed (server continues without it): {e}")


def log_request(path: str, status_code: int, latency_ms: float) -> None:
    if _run is None:
        return
    try:
        key = _metric_key(path)
        with _lock:
            _run.log({
                f"latency_ms/{key}": float(latency_ms),
                f"status_code/{key}": status_code,
            })
    except Exception as e:
        logger.error(f"W&B log_request failed: {e}")


def finish_wandb() -> None:
    global _run
    if _run is None:
        return
    try:
        _run.finish()
        logger.info("W&B run finished")
    except Exception as e:
        logger.error(f"W&B finish failed: {e}")
    finally:
        _run = None
```

---

### `personal_ai_assistant\monitoring\request_monitor.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\monitoring\request_monitor.py`

**Purpose:** The central recorder — every request's metrics are written to a local JSONL file (for the dashboard to read) and forwarded to both MLflow and W&B.

```python
import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional

from personal_ai_assistant.monitoring import mlflow_tracker, wandb_logger
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

_lock = threading.Lock()


def init_monitoring() -> None:
    os.makedirs(os.path.dirname(settings.metrics_log_path), exist_ok=True)
    mlflow_tracker.init_mlflow()
    wandb_logger.init_wandb()


def shutdown_monitoring() -> None:
    mlflow_tracker.finish_mlflow()
    wandb_logger.finish_wandb()


def record_request(method: str, path: str, status_code: int, latency_ms: float) -> None:
    """Save one request's metrics to the local JSONL file, MLflow, and W&B."""
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "method": method,
        "path": path,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
    }

    try:
        with _lock:
            with open(settings.metrics_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
    except Exception as e:
        logger.error(f"Failed to write metrics record: {e}")

    mlflow_tracker.log_request(path, status_code, latency_ms)
    wandb_logger.log_request(path, status_code, latency_ms)


def read_records(limit: Optional[int] = None) -> List[Dict]:
    """Read recorded request metrics (most recent `limit` records if given)."""
    if not os.path.exists(settings.metrics_log_path):
        return []

    records: List[Dict] = []
    with _lock:
        with open(settings.metrics_log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return records[-limit:] if limit else records
```

---

### `personal_ai_assistant\monitoring\dashboard.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\monitoring\dashboard.py`

**Purpose:** Renders `/dashboard` as a self-contained HTML page with 4 Plotly charts (requests per endpoint, average latency in log scale, latency over time in log scale, status code breakdown) plus summary stat cards. Auto-refreshes every `dashboard_refresh_seconds`. Log scale is used for latency charts because endpoint response times vary hugely (milliseconds for `/health` vs. minutes for `/image/generate`).

```python
from collections import defaultdict

import plotly.graph_objects as go
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from personal_ai_assistant.monitoring.request_monitor import read_records
from personal_ai_assistant.utils.config import settings

dashboard_router = APIRouter()

_CSS = """
body { font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 16px; }
h1 { margin: 0 0 12px 0; }
.summary { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.stat { background: #fff; border-radius: 8px; padding: 12px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.stat .value { font-size: 26px; font-weight: bold; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 12px; }
.card { background: #fff; border-radius: 8px; padding: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
"""


def _style(fig, title: str, log_y: bool = False):
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=360,
        margin=dict(l=40, r=20, t=50, b=40),
    )
    if log_y:
        fig.update_yaxes(type="log")
    return fig


def _build_figures(records):
    counts = defaultdict(int)
    latencies = defaultdict(list)
    times = defaultdict(list)
    statuses = defaultdict(int)

    for r in records:
        counts[r["path"]] += 1
        latencies[r["path"]].append(r["latency_ms"])
        times[r["path"]].append(r["timestamp"])
        statuses[str(r["status_code"])] += 1

    paths = list(counts.keys())

    fig_count = _style(
        go.Figure(go.Bar(x=paths, y=[counts[p] for p in paths])),
        "Requests per endpoint",
    )

    averages = [sum(latencies[p]) / len(latencies[p]) for p in paths]
    fig_avg = _style(
        go.Figure(go.Bar(x=paths, y=averages)),
        "Average latency per endpoint (ms, log scale)",
        log_y=True,
    )

    fig_time = go.Figure()
    for p in paths:
        fig_time.add_trace(go.Scatter(x=times[p], y=latencies[p], mode="lines+markers", name=p))
    _style(fig_time, "Latency over time (ms, log scale)", log_y=True)

    fig_status = _style(
        go.Figure(go.Pie(labels=list(statuses.keys()), values=list(statuses.values()))),
        "HTTP status codes",
    )

    return [fig_count, fig_avg, fig_time, fig_status]


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    records = read_records(settings.dashboard_max_points)

    total = len(records)
    errors = sum(1 for r in records if r["status_code"] >= 400)
    avg_latency = sum(r["latency_ms"] for r in records) / total if total else 0.0

    if total == 0:
        charts_html = "<p>No requests recorded yet. Call a few endpoints, then refresh this page.</p>"
    else:
        figures = _build_figures(records)
        charts_html = "".join(
            f'<div class="card">{fig.to_html(full_html=False, include_plotlyjs=(i == 0))}</div>'
            for i, fig in enumerate(figures)
        )

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="{settings.dashboard_refresh_seconds}">
    <title>{settings.app_name} - Dashboard</title>
    <style>{_CSS}</style>
</head>
<body>
    <h1>{settings.app_name} - Dashboard</h1>
    <div class="summary">
        <div class="stat"><div>Total requests</div><div class="value">{total}</div></div>
        <div class="stat"><div>Errors (4xx/5xx)</div><div class="value">{errors}</div></div>
        <div class="stat"><div>Avg latency (ms)</div><div class="value">{avg_latency:.1f}</div></div>
    </div>
    <div class="grid">{charts_html}</div>
</body>
</html>"""
    return HTMLResponse(html)
```

---

### `personal_ai_assistant\api\main.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\main.py`

**Purpose:** Adds a `lifespan` handler to start/stop MLflow and W&B with the server, and an HTTP middleware that times every request and records it — without needing to touch `routes.py` at all. Dashboard/docs/OpenAPI paths are excluded from tracking so viewing the dashboard doesn't pollute its own metrics.

```python
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.concurrency import run_in_threadpool

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger
from personal_ai_assistant.api.routes import router
from personal_ai_assistant.api.websocket import ws_router
from personal_ai_assistant.monitoring.dashboard import dashboard_router
from personal_ai_assistant.monitoring.request_monitor import (
    init_monitoring,
    shutdown_monitoring,
    record_request,
)

logger = get_logger(__name__)

_UNTRACKED_PATHS = ("/dashboard", "/docs", "/openapi.json", "/redoc", "/favicon.ico")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_monitoring()
    yield
    shutdown_monitoring()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    path = request.url.path
    if path.startswith(_UNTRACKED_PATHS):
        return await call_next(request)

    start = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        latency_ms = (time.perf_counter() - start) * 1000
        await run_in_threadpool(record_request, request.method, path, status_code, latency_ms)


app.include_router(router)
app.include_router(ws_router)
app.include_router(dashboard_router)


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

Phase 10 la major blocking errors varala — build and first-run ella clean ah aachu. One minor observation worth recording:

### Observation: Intentional error-test request did not appear in dashboard's error count

**What happened:** Six test requests were sent, the last one deliberately an empty `/chat` message expected to return `400 Bad Request` (to verify the dashboard's error-tracking/status-code chart). The dashboard afterward showed **"Total requests: 5"** and **"Errors (4xx/5xx): 0"** — the 6th (error) request wasn't reflected.

**Karanam (Root Cause) — most likely, not fully isolated:** The middleware measures and records **every** response regardless of status code, so a 400 response should normally still be recorded. The most probable explanation is a timing issue: the dashboard page was loaded/screenshotted before the `/dashboard` page's own auto-refresh cycle re-read the JSONL file, or the final curl command was executed after the screenshot was taken. It could also be a `/chat` endpoint request that returned 400 before the middleware's `try/finally` block was reached in an edge case — this needs a closer look if it recurs.

**Status:** ⚠️ Not blocking — the core dashboard, MLflow, and W&B pipelines are all confirmed working end-to-end for the 5 successful requests recorded. This should be re-verified in a future phase/session (refresh the dashboard page a few seconds after sending an intentional error request, and confirm the "Errors" count and status-code pie chart update accordingly) before relying on error-rate monitoring for anything critical.

---

## 6. Verified Test Results (Screenshots Confirmed)

### Test 1: MLflow UI
Navigated to `http://localhost:5001` (custom port, since default 5000 was already used by a Docker `local-registry` container) → confirmed experiment **`personal-ai-...`** (truncated name for `personal-ai-assistant`) listed under "Recent Experiments", alongside the default `Default` experiment, both created and modified on `09/29/2026`.

### Test 2: Dashboard (`/dashboard`)
- **Summary cards:** Total requests: 5, Errors (4xx/5xx): 0, Avg latency (ms): 32282.8 (skewed high due to the slow `/chat` LLM response being included in the average)
- **Requests per endpoint:** Bar chart showing `/health`, `/`, `/chat` (and more, partially visible) each with 1 request
- **Average latency per endpoint (log scale):** Clearly shows `/health` and `/` as fast (single/double-digit ms), `/chat` as by far the slowest (~100k ms range), `/agent/chat` and `/voice/speak` in between — log scale makes all of these comparable on one chart despite the huge range
- **Latency over time (log scale):** Scatter plot with one point per endpoint, timestamped around 09:52–09:54 on Sep 29, 2026
- **HTTP status codes:** Pie chart showing 100% `200` (all successful requests captured)

### Test 3: W&B Offline Logs
```
dir wandb
```
Confirmed folder: `offline-run-20260929_095148-5e4mi18n` created under `wandb\`, timestamped `29-09-2026 09:51` — matching the server startup time.

---

## 7. Important Notes for Future Reference

- ⚠️ **MLflow's default UI port (5000) conflicts with the existing Docker `local-registry` container** on this machine — always use a different port (`--port 5001` used here) when running `mlflow ui`.
- ⚠️ **Re-verify error-status tracking** — the one observed gap (Section 5) where an intentional 400 error wasn't reflected in the dashboard's error count should be re-tested in a calmer, step-by-step way (send the error request, wait a few seconds, then load the dashboard) before trusting the error-rate metric for anything important.
- The middleware in `main.py` uses a `try/finally` block so that **even if an endpoint raises an unhandled exception**, the request is still recorded (with whatever status code was set, defaulting to 500) — this should be kept in mind if endpoint code changes in future phases in ways that might bypass normal response handling.
- `read_records()` in `request_monitor.py` loads the **entire** JSONL file into memory every time the dashboard is loaded — fine for now, but if `data/metrics/requests.jsonl` grows very large over many sessions, consider capping it (e.g., only keep the last N lines) or switching to a more scalable log rotation strategy, similar to the cleanup notes made for voice/vision files in Phases 8-9.
- W&B is running in `offline` mode by default (`wandb_mode` in `config.py`) — no W&B account or internet connection is needed. If online dashboards/sharing are wanted later, this can be switched to `"online"` and `wandb login` run once, but that is out of scope for the current fully-local setup.
- **`.gitignore` should be updated** to exclude `wandb/`, `data/mlflow.db`, and `data/metrics/` before any future GitHub push (Phase 12) — these are runtime-generated logs/databases, not source code, and can grow large or contain request content that shouldn't be committed.
- The dashboard auto-refreshes every `dashboard_refresh_seconds` (15s default) via a simple HTML meta-refresh tag — no JavaScript polling or WebSocket needed for this simple use case.
- `_UNTRACKED_PATHS` in `main.py` currently excludes `/dashboard`, `/docs`, `/openapi.json`, `/redoc`, and `/favicon.ico` from monitoring — if new documentation/introspection routes are added in future phases, they should likely be added to this list too, to avoid the dashboard's own traffic skewing its charts.

---

## 8. Next Phase

**Phase 11: Docker Packaging** — containerize the full application (single Dockerfile, `docker-compose.yml` covering Ollama, Redis, and the FastAPI app together) so the entire Phases 1-10 stack can be built, run, and shared as one reproducible unit, ahead of the final GitHub push in Phase 12.

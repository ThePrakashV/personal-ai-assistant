# Personal AI Assistant

A fully offline, multi-device conversational AI assistant — inspired by ChatGPT / Gemini / Copilot — built from the ground up using open-source tools. Runs entirely on your own machine via [Ollama](https://ollama.com), with real-time WebSocket streaming, persistent memory, document-based Q&A (RAG), multi-agent workflows, voice, vision, image generation, and a live monitoring dashboard.

---

## ✨ Features

- **Real-time chat** via WebSocket (`/ws/chat`) — token-by-token streaming, multi-device support
- **Short-term memory (CAG)** — Redis-backed conversation history per session
- **Long-term memory (MAG)** — FAISS vector store for semantic recall across sessions, even after a restart
- **RAG (Retrieval-Augmented Generation)** — upload PDF/TXT documents and ask questions grounded in their content
- **Tool-calling agent** — LangGraph-based agent with calculator and real-time date/time tools
- **Multi-agent collaboration** — AutoGen-based team (Researcher, Coder, General) that routes questions to the right specialist
- **Voice I/O** — Whisper (speech-to-text) and pyttsx3 (text-to-speech), fully offline
- **Vision** — image understanding via Ollama's `llava` model
- **Image generation** — text-to-image via Stable Diffusion (`diffusers`)
- **Monitoring dashboard** — Plotly-based `/dashboard` with MLflow + Weights & Biases (offline) tracking underneath
- **Dockerized** — single `docker-compose.yml` for the app + Redis (Ollama runs on the host)

---

## 🏗️ Architecture

```
                         ┌─────────────────────────┐
                         │   Client (Browser /      │
                         │   Mobile / Tablet)        │
                         └────────────┬─────────────┘
                                      │ WebSocket / REST
                         ┌────────────▼─────────────┐
                         │   FastAPI (personal_ai_   │
                         │   assistant/api/)          │
                         │   + Monitoring Middleware   │
                         └────────────┬─────────────┘
                                      │
        ┌──────────────┬─────────────┼─────────────┬───────────────┐
        │              │             │             │               │
 ┌──────▼─────┐ ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐ ┌──────▼──────┐
 │   llm/      │ │  memory/     │ │  rag/     │ │  agents/    │ │ multimodal/  │
 │ Ollama       │ │ Redis (CAG)  │ │ Document  │ │ LangGraph   │ │ Whisper STT   │
 │ (llama3.2)   │ │ FAISS (MAG)  │ │ Loader/   │ │ (tools)     │ │ pyttsx3 TTS   │
 │              │ │              │ │ Chunker/  │ │ AutoGen     │ │ llava Vision  │
 │              │ │              │ │ Embedder/ │ │ (multi-     │ │ Diffusers     │
 │              │ │              │ │ Retriever │ │  agent)     │ │ (image gen)   │
 └──────────────┘ └──────────────┘ └───────────┘ └─────────────┘ └──────────────┘
                                      │
                         ┌────────────▼─────────────┐
                         │      monitoring/           │
                         │  MLflow · W&B · Plotly      │
                         │  request_monitor.py (JSONL) │
                         └───────────────────────────┘
```

**Data flow (typical chat request):** Client → WebSocket/REST → `memory_manager` builds context (short-term Redis history + long-term FAISS recall + RAG document chunks) → sent to Ollama (`llama3.2`) → response streamed back → turn saved to Redis + FAISS → request latency logged to MLflow/W&B/dashboard.

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Backend | FastAPI, Uvicorn, Pydantic |
| LLM Engine | Ollama (`llama3.2`, `llava`) |
| Real-time | WebSocket |
| Short-term Memory | Redis |
| Long-term Memory / RAG | FAISS, Sentence-Transformers |
| Agents | LangChain, LangGraph, AutoGen |
| Voice | OpenAI Whisper (STT), pyttsx3 (TTS) |
| Vision | Ollama `llava` |
| Image Generation | Diffusers (Stable Diffusion), PyTorch |
| Monitoring | MLflow, Weights & Biases, Plotly |
| Containerization | Docker, Docker Compose |

---

## 📋 Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed, with models pulled:
  ```
  ollama pull llama3.2
  ollama pull llava
  ```
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Redis, and optional full containerized run)
- [FFmpeg](https://ffmpeg.org/) (required by Whisper) — Windows: `winget install "FFmpeg (Essentials Build)"`

---

## 🚀 Setup Instructions

### Option A — Run Locally (Python + venv)

```bash
git clone <this-repo-url>
cd personal_ai_assistant_project

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt --prefer-binary

docker run -d --name redis-mem -p 6379:6379 redis
docker update --restart unless-stopped redis-mem

python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- `http://localhost:8000/docs` — Swagger UI (all REST endpoints)
- `http://localhost:8000/dashboard` — monitoring dashboard
- Open `test_client.html` in a browser to test the WebSocket chat directly

### Option B — Run with Docker Compose (app + Redis containerized, Ollama on host)

```bash
ollama list          # confirm llama3.2 and llava are pulled on the host

docker compose build
docker compose up -d
docker compose ps    # confirm both services are "healthy"
```

App available at `http://localhost:8000` (same endpoints as above). Redis is exposed on host port `6380` (internal container-to-container traffic still uses `6379`).

---

## 🔌 Key Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Health/info check |
| `GET /health` | Simple health check |
| `WS /ws/chat` | Real-time streaming chat (memory + RAG aware) |
| `POST /chat` | REST chat (memory + RAG aware) |
| `POST /documents/upload` | Upload a PDF/TXT for RAG |
| `POST /agent/chat` | Single agent with calculator + datetime tools |
| `POST /multiagent/chat` | Multi-agent team (Researcher/Coder/General) |
| `POST /voice/transcribe` | Audio → text (Whisper) |
| `POST /voice/speak` | Text → audio (`.wav`) |
| `POST /vision/analyze` | Image → description (llava) |
| `POST /image/generate` | Text prompt → generated image (`.png`) |
| `GET /dashboard` | Live monitoring dashboard |

Full interactive API docs: `http://localhost:8000/docs`

---

## 📅 Phase Summary

| Phase | What Was Built |
|---|---|
| 1 | Foundation — Ollama, project structure, FastAPI server |
| 2 | Core LLM Engine — Ollama integration, basic `/chat` |
| 3 | WebSocket streaming — real-time, token-by-token responses |
| 4 | Memory Manager — Redis (short-term) + FAISS (long-term) |
| 5 | RAG Pipeline — document upload, chunking, embedding, retrieval |
| 6 | LangGraph Agent — tool-calling (calculator, datetime) |
| 7 | AutoGen Multi-Agent — Researcher/Coder/General team |
| 8 | Voice I/O — Whisper (STT) + pyttsx3 (TTS) |
| 9 | Vision + Image Generation — llava + Stable Diffusion |
| 10 | Dashboard — MLflow, W&B, Plotly monitoring |
| 11 | Docker Packaging — Dockerfile + docker-compose.yml |
| 12 | GitHub push — this README, repo setup |

Detailed per-phase documentation (setup steps, full code, errors faced and fixes, verified test results) is available in `PHASE1_FOUNDATION_SETUP.md` through `PHASE11_DOCKER_PACKAGING.md`.

---

## 📁 Project Structure

```
personal_ai_assistant_project/
├── personal_ai_assistant/
│   ├── llm/            # Ollama client, inference
│   ├── memory/         # Redis (CAG) + FAISS (MAG)
│   ├── rag/            # Document loader, chunker, embedder, retriever
│   ├── agents/         # LangGraph + AutoGen agents
│   ├── multimodal/     # Whisper STT, TTS, vision, image generation
│   ├── monitoring/     # MLflow, W&B, request monitor, dashboard
│   ├── api/            # FastAPI app, routes, WebSocket, schemas
│   └── utils/          # Config, logger
├── data/                # Runtime data (gitignored)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚠️ Notes

- All AI processing runs **fully offline/locally** via Ollama — no external API keys or internet connection required after initial model downloads.
- Image generation on CPU (no GPU) takes several minutes per image — this is expected.
- `data/`, `wandb/`, and `.env` are excluded from version control (see `.gitignore`).

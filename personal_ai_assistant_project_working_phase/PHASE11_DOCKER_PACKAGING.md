# Phase 11: Docker Packaging (Single Dockerfile + docker-compose.yml)

## Status: ✅ Complete
**Date:** 29-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 10 varaikkum project unga laptop-la venv-oda mattum run aayiduchu. Phase 11 la muzhu app-a **Docker containers-la package** pannoam, evlo machine-layum reproducible ah run panna:

1. `.dockerignore` create pannoam — `venv/`, `data/`, `wandb/`, `.git/` maadhiri runtime/dev-only files-a Docker image-la irundhu exclude panna.
2. **Dockerfile** create pannoam — Python 3.11-slim base image, system dependencies (ffmpeg for Whisper, build-essential), Python dependencies, app code, healthcheck.
3. **docker-compose.yml** create pannoam — `app` (FastAPI) + `redis` rendu services define panni.
4. **Key architectural decision:** Ollama models (llama3.2, llava — already 6-7GB combined, host-la download pannirukom) container-kulla mீndum download panna vendaam nu, **Ollama host machine-layae run aagum**, container app `host.docker.internal` மூலமா connect aagum. App + Redis mattum containerize pannoam.
5. Redis container host-side port **6380** use pannoam (6379 illa) — yean na existing `redis-mem` container (Phase 4-la vachadhu) already 6379 use pannudhu, port conflict avoid panna.
6. **Docker Hub network timeout** debug panni fix pannoam (simple retry solved it).
7. Build + run + test — `docker compose ps` rendu containers-um "healthy" status-la confirm pannoam, `/health`, `/`, `/chat` endpoints test panni, `/dashboard` container-oda traffic correctly track panni kaattuchu.

**Result:** Namma entire Phases 1-10 stack ippo **`docker compose up -d`** oru command-la start aagum — app + Redis containerized, Ollama host-la reused, data persistence volumes மூலமா maintain aagும். Project ippo evlo laptop/server-layum "docker compose up" mூலமா reproducible ah deploy panna ready.

---

## 2. Full Folder Structure (Phase 11 end state — new/updated marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\           (unchanged — all Phase 1-10 code)
│   ├── ...
├── data\                            (mounted as Docker volume, persists outside containers)
│   ├── documents\
│   ├── voice\
│   ├── vision\
│   ├── generated_images\
│   ├── metrics\
│   ├── mlflow.db
│   ├── faiss_memory.index
│   ├── faiss_metadata.pkl
│   ├── rag_index.index
│   └── rag_metadata.pkl
├── wandb\                           (mounted as Docker volume)
├── venv\                          (excluded from Docker image via .dockerignore)
├── requirements.txt
├── Dockerfile                       ← NEW (Phase 11)
├── docker-compose.yml               ← NEW (Phase 11)
├── .dockerignore                    ← NEW (Phase 11)
├── test_client.html
├── setup.py
├── pyproject.toml
├── .env                           (local dev only — not used inside containers)
├── .gitignore
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Create `.dockerignore`
```
type nul > .dockerignore
notepad .dockerignore
```

### Step 2 — Create `Dockerfile`
```
type nul > Dockerfile
notepad Dockerfile
```

### Step 3 — Create `docker-compose.yml`
```
type nul > docker-compose.yml
notepad docker-compose.yml
```

### Step 4 — Verify Ollama Is Running on the Host (not in Docker)
```
ollama list
```

### Step 5 — Build the Image (first attempt — hit a network timeout, see Section 5)
```
docker compose build
```

### Step 6 — Retry Build (succeeded)
```
docker compose build
```

### Step 7 — Start Containers
```
docker compose up -d
```

### Step 8 — Verify Container Status
```
docker compose ps
```

### Step 9 — Check App Logs
```
docker compose logs -f app
```

### Step 10 — Test Endpoints (separate CMD window)
```
curl http://localhost:8000/health
curl http://localhost:8000/
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Hello from Docker\"}"
```

### Step 11 — Verify Dashboard Reflects Containerized Traffic
```
http://localhost:8000/dashboard
```

---

## 4. Full File Contents (Final Working Code)

### `.dockerignore`
**Path:** `D:\project\personal_ai_assistant_project\.dockerignore`
```
venv/
__pycache__/
*.pyc
.env
*.log
data/
wandb/
.git/
.gitignore
test_client.html
*.wav
*.png
```

---

### `Dockerfile`
**Path:** `D:\project\personal_ai_assistant_project\Dockerfile`

**Purpose:** Builds the FastAPI app image — installs system dependencies (ffmpeg for Whisper), Python dependencies (cached as a separate layer for faster rebuilds), copies application code, sets up runtime data folders, and defines a health check.

```dockerfile
FROM python:3.11-slim

# System dependencies: ffmpeg for Whisper, build tools for some Python packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better Docker layer caching —
# this layer only rebuilds if requirements.txt changes, not on every code edit)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy application code
COPY personal_ai_assistant/ ./personal_ai_assistant/
COPY setup.py pyproject.toml ./

# Create runtime data directories (mounted as volumes in docker-compose, but
# created here too so the app doesn't fail if run standalone without compose)
RUN mkdir -p data/documents data/voice data/vision data/generated_images data/metrics

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "personal_ai_assistant.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Note:** The `--reload` flag used during development (Phases 1-10) is intentionally **not** included here — auto-reload is a development convenience with extra file-watching overhead, not appropriate for a packaged/production container.

---

### `docker-compose.yml`
**Path:** `D:\project\personal_ai_assistant_project\docker-compose.yml`

**Purpose:** Defines and wires together the `app` and `redis` services. The app connects to Ollama running on the **host machine** (not containerized) via `host.docker.internal`, avoiding the need to re-download large Ollama models (`llama3.2`, `llava`) inside a container.

```yaml
services:
  app:
    build: .
    container_name: personal-ai-assistant-app
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - ./data:/app/data
      - ./wandb:/app/wandb
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

  redis:
    image: redis
    container_name: redis-mem-docker
    ports:
      - "6380:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
```

**Key design notes:**
- `OLLAMA_BASE_URL`, `REDIS_HOST`, `REDIS_PORT` are picked up automatically by `pydantic_settings.BaseSettings` in `utils/config.py` (already set up since Phase 1) — **no code changes were needed** for Docker environment overrides to work.
- Redis's **host-side** port is mapped to `6380` (not `6379`), because the existing `redis-mem` Docker container from Phase 4 already occupies host port `6379`. Container-to-container communication (`app` → `redis`) still uses the internal port `6379` via the service name `redis`, so this only affects access *from the host machine*, not from within the compose network.
- `./data` and `./wandb` are mounted as volumes so that FAISS indexes, uploaded documents, generated images, metrics, and W&B logs all **persist on the host** even if containers are removed and recreated.

---

## 5. Errors Faced & How We Solved Them

### Error 1: `net/http: TLS handshake timeout` while pulling the base image

**Exact error seen:**
```
#3 ERROR: failed to do request: Head "https://registry-1.docker.io/v2/library/python/manifests/3.11-slim": net/http: TLS handshake timeout
failed to solve: python:3.11-slim: failed to resolve source metadata for docker.io/library/python:3.11-slim: failed to do request: ... TLS handshake timeout
```

**Karanam (Root Cause):** This was a transient network connectivity issue between Docker Desktop and Docker Hub (`registry-1.docker.io`) — the TLS handshake with Docker's registry server timed out, likely due to a temporary internet slowdown or connection hiccup. This was unrelated to the `Dockerfile` or `docker-compose.yml` content itself.

**Analogy:** Namma "ingredient supplier" (Docker Hub) kூрра call pண்ணினோம், aana connection **timeout** aachu — namma recipe (Dockerfile) correct ah irundhaলும், call itself connect aagala.

**Fix:** Simply retried the same command:
```
docker compose build
```

**Status:** ✅ Resolved on retry — the second build attempt succeeded without any changes to configuration, confirming this was a one-off network blip rather than a persistent issue. (No Docker Desktop restart or DNS troubleshooting was needed in this case, though those were prepared as fallback steps if the simple retry hadn't worked.)

---

## 6. Verified Test Results (Screenshots Confirmed)

### Test 1: Container Health Status
```
docker compose ps
```
```
NAME                      IMAGE                             SERVICE   STATUS                    PORTS
personal-ai-assistant-app personal_ai_assistant_project-app app       Up 14 minutes (healthy)   0.0.0.0:8000->8000/tcp
redis-mem-docker          redis                             redis     Up 15 minutes (healthy)   0.0.0.0:6380->6379/tcp
```
Both `app` and `redis` services confirmed **"healthy"**.

### Test 2: Endpoint Tests (from host, against containerized app)
```
curl http://localhost:8000/health
{"status":"ok"}

curl http://localhost:8000/
{"message":"Personal AI Assistant is running!","app_name":"Personal AI Assistant","configured_model":"llama3.2"}

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Hello from Docker\"}"
{"reply":"Hello from the other side... of the Docker container! It seems like you're running from within the `redis-mem` container. How can I assist you today?"}
```
All three requests succeeded with `200 OK`. (The LLM's reply playfully mentioning "redis-mem container" is just conversational flavor from the model — not a real error; the app correctly runs in its own `app` container, connects to the separate `redis` service, and to Ollama on the host.)

### Test 3: Dashboard Reflects Containerized Traffic
`http://localhost:8000/dashboard` — confirmed 32 total requests tracked, 0 errors, with the "Requests per endpoint", "Average latency", "Latency over time", and "HTTP status codes" charts all populated correctly, proving the Phase 10 monitoring stack (JSONL logging, MLflow, W&B) works identically inside the Docker container as it did running directly via `uvicorn`.

### Test 4: Container Logs Confirm Full Startup Sequence
`docker compose logs` showed the complete expected startup sequence inside the container: W&B offline run initialization, `Application startup complete`, `Uvicorn running on http://0.0.0.0:8000`, followed by a stream of successful `GET /health`, `GET /`, `POST /chat`, and `GET /dashboard` requests — confirming the containerized app behaves identically to the host-run version from all previous phases.

---

## 7. Important Notes for Future Reference

- ⚠️ **Ollama is intentionally NOT containerized** — it must be running on the host machine (`ollama list` should show the models before starting Docker containers) for the app container to successfully reach it via `http://host.docker.internal:11434`. This was a deliberate choice to avoid re-downloading multi-gigabyte models inside a container.
- ⚠️ **Redis host-side port is `6380`, not `6379`** — this only matters if connecting to Redis directly from the host (e.g., `redis-cli -p 6380`); the app-to-redis connection inside the Docker network still uses the standard `6379` via the `redis` service hostname.
- A network timeout while pulling a base image (Error 1) is usually transient — **retry the build command first** before investigating Docker Desktop settings, DNS, or firewall/VPN configuration.
- `data/` and `wandb/` are mounted as **volumes**, not baked into the image — this means `docker compose down` (without `-v`) followed by `docker compose up -d` again will **preserve** all FAISS indexes, uploaded documents, generated images, metrics history, and MLflow/W&B data. Only `docker compose down -v` (explicitly removing volumes) would wipe this data — this should be avoided unless a clean reset is genuinely intended.
- The `Dockerfile`'s Python dependency installation is placed in its own layer (before copying application code) specifically so that **code-only changes rebuild fast** — Docker's layer cache skips re-running `pip install` unless `requirements.txt` itself changes.
- The container's `HEALTHCHECK` (hitting `/health` every 30s) is what allows `docker compose ps` to report "healthy" and what `depends_on: redis: condition: service_healthy` relies on to ensure Redis is ready before the app container starts.
- For any future deployment to a different machine, the only host-side prerequisite is Ollama running with the required models pulled (`llama3.2`, `llava`) — everything else (Redis, the FastAPI app, all Python dependencies) is fully contained within `docker compose up -d`.

---

## 8. Next Phase

**Phase 12: GitHub Push** — prepare the full project for its first GitHub push: repo name suggestions, GitHub "About" description and topics/tags, a complete `README.md` (architecture diagram, features, tech stack, setup instructions, phase summary table), step-by-step git commands, and verification that `.env`/`.gitignore` properly exclude all secrets and runtime-generated files (including the new `wandb/`, `data/mlflow.db`, and `data/metrics/` noted in Phase 10).

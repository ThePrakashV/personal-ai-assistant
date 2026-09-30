# Phase 9: Vision + Image Generation (Image Understanding + Diffusers)

## Status: ✅ Complete
**Date:** 27-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 8 la assistant-kku audio capabilities (STT/TTS) kொடுthோம். Phase 9 la assistant-kku **visual capabilities** add pண்ணினோம் — image understanding (Vision) matrும் image creation (Generation):

1. **Ollama vision model** (`llava`, ~4.7GB) pull pண்ணினோம் — existing Ollama setup-a reuse pண்ணி, images "பார்th்து" describe pண்ண.
2. `requirements.txt` la `diffusers`, `accelerate`, `pillow` add pண்ணினோம் — Stable Diffusion mூலமா text-to-image generation ku.
3. `utils/config.py` la vision + image-gen settings add pண்ணினோம் (model names, output folders, inference steps, image dimensions).
4. `multimodal/llava_vision.py` create pண்ணினோம் — image path கொடுthா, `llava` model mூலமா detailed description tharும்.
5. `multimodal/diffusers_gen.py` create pண்ணினோம் — text prompt கொடுthா, Stable Diffusion pipeline (lazy-loaded, CPU/GPU auto-detect) மூலமா `.png` image generate pண்ணி save pண்ணும்.
6. Rendு புதிய endpoints add pண்ணினோம் — `POST /vision/analyze` (image upload → description) matrும் `POST /image/generate` (text prompt → downloadable `.png`).
7. **Missing file issue** (Phase 8-la paatha same pattern) மீண்டும் kண்டுபிடித்து fix pண்ணினோம் — vision testing-ku actual image file `data/vision/` folder-la illama irundhуchу.
8. **First-time model download wait** (Stable Diffusion, ~1.22GB) patiently handle pண்ணினோம், appuram successful image generation confirm pண்ணினோம்.

**Result:** Assistant ippo **image-in, image-out** capability vachirukku. Vision test-la, oru "Robotics Development Kit" banner image-a `llava` model **highly detailed and accurate ah** describe pண்ணிyачு (colors, text, layout, QR code, character identity ellame). Image generation test-la, "a cute robot reading a book, digital art" prompt-ku, Stable Diffusion **visually accurate, high-quality** matching image create pண்ணிyачу.

---

## 2. Full Folder Structure (Phase 9 end state — new/updated marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── utils\
│   │   ├── __init__.py
│   │   ├── config.py               ← UPDATED (vision + image-gen settings added)
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
│   │   ├── langchain_agent.py
│   │   ├── langgraph_workflow.py
│   │   └── autogen_agent.py
│   ├── multimodal\
│   │   ├── __init__.py
│   │   ├── whisper_stt.py          (Phase 8)
│   │   ├── tts_engine.py           (Phase 8)
│   │   ├── llava_vision.py         ← NEW (Phase 9 — image understanding)
│   │   └── diffusers_gen.py        ← NEW (Phase 9 — image generation)
│   └── api\
│       ├── __init__.py
│       ├── main.py
│       ├── routes.py                ← UPDATED (/vision/analyze, /image/generate added)
│       ├── schemas.py
│       └── websocket.py
├── data\
│   ├── documents\
│   │   └── company_policy.txt
│   ├── voice\
│   │   └── (Phase 8 audio files)
│   ├── vision\                     ← NEW (uploaded images for analysis)
│   │   └── (test images copied here)
│   ├── generated_images\           ← NEW (Diffusers output)
│   │   └── gen_<uuid>.png
│   ├── faiss_memory.index
│   ├── faiss_metadata.pkl
│   ├── rag_index.index
│   └── rag_metadata.pkl
├── venv\                          (excluded from git)
├── requirements.txt                ← UPDATED (diffusers, accelerate, pillow added)
├── test_client.html
├── setup.py
├── pyproject.toml
├── .env                           (excluded from git)
├── .gitignore
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Download Ollama Vision Model
```
ollama pull llava
ollama list
```

### Step 2 — Update Dependencies
```
pip install -r requirements.txt --prefer-binary
```

### Step 3 — Create Folders
```
mkdir data\vision
mkdir data\generated_images
```

### Step 4 — Verify Every File Before Running
```
python -m py_compile personal_ai_assistant\utils\config.py
python -m py_compile personal_ai_assistant\multimodal\llava_vision.py
python -m py_compile personal_ai_assistant\multimodal\diffusers_gen.py
python -m py_compile personal_ai_assistant\api\routes.py
```

### Step 5 — Run Server
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6 — Test Image Generation (triggers first-time Stable Diffusion download, ~1.22GB)
```
curl -X POST http://localhost:8000/image/generate -H "Content-Type: application/json" -d "{\"prompt\": \"a cute robot reading a book, digital art\"}" --output data/generated_images/test_output.png
```

### Step 7 — Test Vision Analysis (via Swagger UI — avoids file-path issues)
`http://localhost:8000/docs` → `POST /vision/analyze` → Try it out → Choose File (any image from computer) → Execute

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
```

---

### `personal_ai_assistant\utils\config.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\utils\config.py`

**Purpose:** Added Vision (which Ollama vision model to use) and Image Generation (Stable Diffusion model, output settings, inference steps/dimensions) settings.

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

    class Config:
        env_file = ".env"


settings = Settings()
```

---

### `personal_ai_assistant\multimodal\llava_vision.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\multimodal\llava_vision.py`

**Purpose:** Sends an image to Ollama's `llava` vision model and returns its description/analysis — reuses the existing Ollama server, no separate vision framework needed.

```python
import ollama

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def analyze_image(image_path: str, question: str = "Describe this image in detail.") -> str:
    """Send an image to the Ollama vision model (llava) and return its description/answer."""
    logger.info(f"Analyzing image: {image_path}")

    client = ollama.Client(host=settings.ollama_base_url)
    response = client.chat(
        model=settings.vision_model,
        messages=[
            {
                "role": "user",
                "content": question,
                "images": [image_path],
            }
        ],
    )

    description = response["message"]["content"]
    logger.info(f"Vision analysis result: {description[:60]}...")
    return description
```

---

### `personal_ai_assistant\multimodal\diffusers_gen.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\multimodal\diffusers_gen.py`

**Purpose:** Generates an image from a text prompt using Stable Diffusion (via `diffusers`), auto-detecting CPU vs GPU, and lazily loading the (large) pipeline only on first actual use so server startup stays fast.

```python
import os
import uuid

import torch
from diffusers import StableDiffusionPipeline

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

_device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Image generation will run on: {_device}")

_pipeline = None  # lazy-loaded on first use (avoids slowing down server startup)


def _get_pipeline() -> StableDiffusionPipeline:
    global _pipeline
    if _pipeline is None:
        logger.info(f"Loading image generation model: {settings.image_gen_model} (first call — may take a while)")
        dtype = torch.float16 if _device == "cuda" else torch.float32
        _pipeline = StableDiffusionPipeline.from_pretrained(settings.image_gen_model, torch_dtype=dtype)
        _pipeline = _pipeline.to(_device)
    return _pipeline


def generate_image(prompt: str) -> str:
    """Generate an image from a text prompt and return the saved file path."""
    pipeline = _get_pipeline()

    logger.info(f"Generating image for prompt: {prompt[:50]}...")
    result = pipeline(
        prompt,
        num_inference_steps=settings.image_gen_steps,
        width=settings.image_gen_width,
        height=settings.image_gen_height,
    )
    image = result.images[0]

    os.makedirs(settings.image_gen_output_folder, exist_ok=True)
    filename = f"gen_{uuid.uuid4().hex}.png"
    output_path = os.path.join(settings.image_gen_output_folder, filename)
    image.save(output_path)

    logger.info(f"Image saved to: {output_path}")
    return output_path
```

**Note:** `_pipeline` is deliberately lazy-loaded (`None` until first actual `/image/generate` call) rather than loaded at import time — this keeps server startup fast even though Whisper, embedding models, and Stable Diffusion are all part of the same project; Stable Diffusion only loads when actually needed.

---

### `personal_ai_assistant\api\routes.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\routes.py`

**Purpose:** Added `POST /vision/analyze` (image upload → text description) and `POST /image/generate` (text prompt → downloadable `.png` via `FileResponse`).

```python
import os
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from personal_ai_assistant.api.schemas import (
    ChatRequest, ChatResponse, IngestResponse,
    AgentRequest, AgentResponse,
    MultiAgentRequest, MultiAgentResponse,
)
from personal_ai_assistant.llm.inference import generate_response
from personal_ai_assistant.rag.retriever import rag_retriever
from personal_ai_assistant.agents.langgraph_workflow import run_agent
from personal_ai_assistant.agents.autogen_agent import run_multiagent
from personal_ai_assistant.multimodal.whisper_stt import transcribe_audio
from personal_ai_assistant.multimodal.tts_engine import text_to_speech
from personal_ai_assistant.multimodal.llava_vision import analyze_image
from personal_ai_assistant.multimodal.diffusers_gen import generate_image
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class TranscribeResponse(BaseModel):
    text: str


class SpeakRequest(BaseModel):
    text: str


class VisionResponse(BaseModel):
    description: str


class ImageGenRequest(BaseModel):
    prompt: str


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


@router.post("/voice/transcribe", response_model=TranscribeResponse)
def voice_transcribe(file: UploadFile = File(...)):
    os.makedirs(settings.voice_temp_folder, exist_ok=True)
    save_path = os.path.join(settings.voice_temp_folder, file.filename)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = transcribe_audio(save_path)
        return TranscribeResponse(text=text)

    except Exception as e:
        logger.error(f"Voice transcription failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")


@router.post("/voice/speak")
def voice_speak(request: SpeakRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        audio_path = text_to_speech(request.text)
        return FileResponse(audio_path, media_type="audio/wav", filename="response.wav")

    except Exception as e:
        logger.error(f"Text-to-speech failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate speech")


@router.post("/vision/analyze", response_model=VisionResponse)
def vision_analyze(file: UploadFile = File(...)):
    os.makedirs(settings.vision_temp_folder, exist_ok=True)
    save_path = os.path.join(settings.vision_temp_folder, file.filename)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        description = analyze_image(save_path)
        return VisionResponse(description=description)

    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")


@router.post("/image/generate")
def image_generate(request: ImageGenRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        image_path = generate_image(request.prompt)
        return FileResponse(image_path, media_type="image/png", filename="generated.png")

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image")
```

---

## 5. Errors Faced & How We Solved Them

### Error 1: `curl: (26) Failed to open/read local data from file/application` (vision test — recurring pattern from Phase 8)

**Exact error seen:**
```
curl -X POST http://localhost:8000/vision/analyze -F "file=@data/vision/test_image.jpg"
curl: (26) Failed to open/read local data from file/application
```

**Karanam (Root Cause):** Same root cause as Phase 8's Error 1 — `data/vision/test_image.jpg` simply did not exist yet. No image had actually been placed in the `data\vision\` folder before the curl command referenced it.

**Analogy:** Namma curl-kku "andha file-a upload pண்ணு" nு solрром், aana andha file existeye illa.

**Fix:** Instead of continuing with curl (which requires an exact pre-existing file path), switched to **Swagger UI's file browser**:
`http://localhost:8000/docs` → `POST /vision/analyze` → Try it out → "Choose File" → selected an actual image directly from the computer (no need to pre-copy it into a specific project folder) → Execute.

**Status:** ✅ Resolved — Swagger UI's native file browser sidesteps the "does this exact path exist" problem entirely, since it lets the user pick any file on their system directly. Returned a detailed, accurate description of the test image (a "Robotics Development Kit" banner graphic).

---

### Error 2 (Not an error — expected first-time delay): Image generation appeared to "hang" during first call

**What happened:** The `curl -X POST .../image/generate ...` command showed a progress bar with "Time Left" counting down, and took several minutes total before returning a result.

**Karanam (Root Cause):** This was **not an error** — it was the expected one-time download and setup of the Stable Diffusion model (`runwayml/stable-diffusion-v1-5`, ~1.22GB total across 15 files), followed by loading pipeline weights, then running 25 inference steps on CPU (no GPU available on this machine). Server logs confirmed the full sequence: `Fetching 15 files: 100%` → `Download complete` → `Reconstruction complete` → `Loading weights: 100%` (×2) → `Loading pipeline components: 100%` → `Generating image... 100%` (25/25 steps, ~3 min 15 sec) → `Image saved to: data/generated_images/gen_f1d0b13876174ae08e4a8648c8106141.png` → `200 OK`.

**Status:** ✅ Not an error — confirmed as expected first-time model download + CPU-based generation time. Subsequent calls will skip the download step (model cached locally) but will still take a few minutes per image on CPU, since no GPU is available.

---

## 6. Verified Test Results (Screenshots Confirmed)

### Test 1: Vision Analysis
**Input:** A "Robotics Development Kit" promotional banner image.
**Response:**
> "The image is a digital graphic, likely a web banner or promotional material for a 'Robotics Development Kit.' It features a vibrant blue background with a grid of cells... In the center, there's a prominent graphic of a robot resembling B-Bop... The robot is colored blue and is depicted in a standing position... 'ALL IN ONE!' is written in bold, capitalized letters... To the right of the robot, there's a QR code and a text that reads 'scan to get your kit.'..." (full response continued with further accurate details about text labels, layout, and purpose)

**Confirmed:** Highly detailed and accurate description, correctly identifying colors, layout, text content, a QR code, and even a character resemblance — demonstrates strong vision understanding from the `llava` model.

### Test 2: Image Generation
**Prompt:** `"a cute robot reading a book, digital art"`
**Result:** A `.png` image was generated and saved, then manually opened and visually confirmed — a colorful digital-art-style robot character (large orange eyes, gray/purple metallic body) holding open a teal book, on a yellow/teal diagonal-striped background. The image closely matched the intent of the text prompt.

**Server log confirmation:**
```
personal_ai_assistant.multimodal.diffusers_gen | INFO | Image saved to: data/generated_images/gen_f1d0b13876174ae08e4a8648c8106141.png
INFO: 127.0.0.1:54207 - "POST /image/generate HTTP/1.1" 200 OK
```

---

## 7. Important Notes for Future Reference

- ⚠️ **Same lesson as Phase 8 applies here:** always verify a referenced file actually exists before using it in a `curl -F "file=@..."` command. For any file-upload testing going forward, **Swagger UI's "Choose File" browser is more reliable** than manually managing exact file paths via curl.
- ⚠️ **Image generation is slow on CPU** (~3+ minutes per image with default 25 inference steps at 512×512) — this is expected without a GPU. If speed becomes important later, consider: reducing `image_gen_steps` in `config.py` (fewer steps = faster but lower quality), using a smaller/faster model, or running on a machine with a CUDA-capable GPU (the code already auto-detects and uses GPU via `torch.cuda.is_available()` if present).
- The Stable Diffusion model (~1.22GB) is downloaded **once** and cached locally by Hugging Face's library — subsequent server restarts will not re-download it, only the first-ever `/image/generate` call triggers the download.
- `_pipeline` in `diffusers_gen.py` is lazy-loaded (not loaded at server startup) — this keeps `uvicorn` startup fast even with Whisper + embedding models + Stable Diffusion all part of the same project; Stable Diffusion only loads into memory on the first actual generation request.
- `llava` (vision model, ~4.7GB) runs through the same local Ollama server as `llama3.2` — no separate vision framework or additional infrastructure was needed, keeping the stack simple.
- Both `/vision/analyze` and `/image/generate` are currently **standalone** endpoints, not yet integrated with memory (Phase 4), RAG (Phase 5), or the agent workflows (Phase 6/7) — consistent with the pattern from Phase 6-8, where each new capability is verified in isolation before any future consolidation phase.
- Generated images (`data/generated_images/`) and analyzed images (`data/vision/`) are **not automatically cleaned up** — consider adding cleanup logic in a future phase if disk usage becomes a concern, similar to the note made for voice files in Phase 8.

---

## 8. Next Phase

**Phase 10: Dashboard** — build monitoring and observability using MLflow, Weights & Biases (W&B), and Plotly, so the various pipelines (LLM calls, memory, RAG, agents, voice, vision, image generation) built across Phases 1-9 can be tracked, visualized, and debugged more easily.

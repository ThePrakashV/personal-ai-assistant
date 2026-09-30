# Phase 8: Voice Input/Output (Whisper STT + TTS)

## Status: ✅ Complete
**Date:** 27-09-2026
**Project:** Personal Multi-Device AI Assistant (like ChatGPT/Gemini/Copilot)

---

## 1. Summary — Enna Pannoam

Phase 7 vare assistant text mattум் handle pண்ணிyachu. Phase 8 la assistant-kku **voice capabilities** add pண்ணினோம் — Whisper (Speech-to-Text) matrும் pyttsx3 (Text-to-Speech), rendும் **fully offline**:

1. Puthusa `multimodal/` package create pண்ணினோம் — `whisper_stt.py` (audio → text) matrும் `tts_engine.py` (text → audio).
2. **FFmpeg** (system-level tool, Whisper-ku mandatory) install pண்ணினோம் — `winget` mூலமா.
3. `requirements.txt` la `openai-whisper` (offline STT, PyTorch-based) matrும் `pyttsx3` (offline TTS, Windows SAPI5 voices use pண்ணுthu) add pண்ணினோம்.
4. `utils/config.py` la voice settings add pண்ணினோம் (Whisper model size, TTS rate/volume, temp folder).
5. Rendு puthுsa endpoints add pண்ணினோம் — `POST /voice/transcribe` (audio upload → text) matrும் `POST /voice/speak` (text → downloadable `.wav` audio file, `FileResponse` mூலமா).
6. Testing-la **real microphone recording கிடைக்காத** situation-a handle pண்ண, oru **smart "self-test loop"** approach use pண்ணினோம் — namma own TTS endpoint-a vachi audio generate pண்ணி, andha audio-a namma own STT endpoint-கே feed pண்ணி, rendையும் oрே vாттம் verify pண்ணினோம்.
7. Journey-la file-path related curl errors (missing recording file) debug pண்ணினோம், matrும் andha issue-a "TTS-generated audio use pண்ணுradhு" nு workaround pண்ணினோம்.

**Result:** Assistant ippo **audio-in, audio-out** capability vachirukku. `/voice/speak` correct ah text-a `.wav` audio ah convert pண்ணிyachu, `/voice/transcribe` andha same audio-a thiруmba **exact ah correct text** ah (question mark கூட correctly) transcribe pண்ணிyачு — end-to-end voice pipeline confirmed.

---

## 2. Full Folder Structure (Phase 8 end state — new/updated marked)

```
D:\project\personal_ai_assistant_project\
├── personal_ai_assistant\
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── utils\
│   │   ├── __init__.py
│   │   ├── config.py               ← UPDATED (voice settings added)
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
│   ├── multimodal\                 ← NEW (Phase 8)
│   │   ├── __init__.py
│   │   ├── whisper_stt.py          ← NEW (Speech-to-Text)
│   │   └── tts_engine.py           ← NEW (Text-to-Speech)
│   └── api\
│       ├── __init__.py
│       ├── main.py
│       ├── routes.py                ← UPDATED (/voice/transcribe, /voice/speak added)
│       ├── schemas.py
│       └── websocket.py
├── data\
│   ├── documents\
│   │   └── company_policy.txt
│   ├── voice\                      ← NEW (voice files temp storage)
│   │   ├── test_voice.wav          ← NEW (TTS-generated test audio)
│   │   └── tts_<uuid>.wav          ← NEW (per-request TTS output files)
│   ├── faiss_memory.index
│   ├── faiss_metadata.pkl
│   ├── rag_index.index
│   └── rag_metadata.pkl
├── venv\                          (excluded from git)
├── requirements.txt                ← UPDATED (openai-whisper, pyttsx3 added)
├── test_client.html
├── setup.py
├── pyproject.toml
├── .env                           (excluded from git)
├── .gitignore
└── README.md
```

---

## 3. Step-by-Step Commands (Exact Order Followed)

### Step 1 — Install FFmpeg (system-level, required by Whisper)
```
winget install "FFmpeg (Essentials Build)"
```
Then, in a fresh CMD window (to refresh PATH):
```
ffmpeg -version
```

### Step 2 — Create `multimodal/` Package
```
mkdir personal_ai_assistant\multimodal
type nul > personal_ai_assistant\multimodal\__init__.py
type nul > personal_ai_assistant\multimodal\whisper_stt.py
type nul > personal_ai_assistant\multimodal\tts_engine.py
mkdir data\voice
```

### Step 3 — Update Dependencies
```
pip install -r requirements.txt --prefer-binary
```

### Step 4 — Verify Every File Before Running
```
python -m py_compile personal_ai_assistant\utils\config.py
python -m py_compile personal_ai_assistant\multimodal\whisper_stt.py
python -m py_compile personal_ai_assistant\multimodal\tts_engine.py
python -m py_compile personal_ai_assistant\api\routes.py
```

### Step 5 — Run Server
```
python -m uvicorn personal_ai_assistant.api.main:app --reload --host 0.0.0.0 --port 8000
```
(Whisper `base` model, 139MB, downloads on first run — confirmed in logs.)

### Step 6 — Test: Generate Audio via TTS (self-test workaround — see Section 5)
```
curl -X POST http://localhost:8000/voice/speak -H "Content-Type: application/json" -d "{\"text\": \"What is the capital of France\"}" --output data/voice/test_voice.wav
```

### Step 7 — Verify File Was Created
```
dir data\voice
```

### Step 8 — Test: Transcribe the Generated Audio
```
curl -X POST http://localhost:8000/voice/transcribe -F "file=@data/voice/test_voice.wav"
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
```

---

### `personal_ai_assistant\utils\config.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\utils\config.py`

**Purpose:** Added voice-related settings — which Whisper model size to load, where temporary voice files are stored, and TTS speech rate/volume.

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

    class Config:
        env_file = ".env"


settings = Settings()
```

---

### `personal_ai_assistant\multimodal\whisper_stt.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\multimodal\whisper_stt.py`

**Purpose:** Loads a Whisper model once at startup and provides a function to transcribe any audio file to text — runs fully offline after the initial one-time model download.

```python
import whisper

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

logger.info(f"Loading Whisper model: {settings.whisper_model_size}")
_whisper_model = whisper.load_model(settings.whisper_model_size)


def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file to text using Whisper (runs fully offline)."""
    logger.info(f"Transcribing audio: {file_path}")
    result = _whisper_model.transcribe(file_path)
    text = result.get("text", "").strip()
    logger.info(f"Transcription result: {text[:60]}...")
    return text
```

---

### `personal_ai_assistant\multimodal\tts_engine.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\multimodal\tts_engine.py`

**Purpose:** Converts text into a spoken `.wav` file using `pyttsx3` (offline, uses Windows SAPI5 voices) and returns the saved file's path.

```python
import os
import uuid

import pyttsx3

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def text_to_speech(text: str) -> str:
    """Convert text to a spoken .wav audio file (fully offline) and return the file path."""
    os.makedirs(settings.voice_temp_folder, exist_ok=True)

    filename = f"tts_{uuid.uuid4().hex}.wav"
    output_path = os.path.join(settings.voice_temp_folder, filename)

    logger.info(f"Generating speech for: {text[:50]}...")

    engine = pyttsx3.init()
    engine.setProperty("rate", settings.tts_rate)
    engine.setProperty("volume", settings.tts_volume)
    engine.save_to_file(text, output_path)
    engine.runAndWait()

    logger.info(f"Speech saved to: {output_path}")
    return output_path
```

**Note:** A fresh `pyttsx3.init()` engine instance is created on every call rather than reusing a single global instance — this avoids known threading/state issues where a reused `pyttsx3` engine can silently fail to produce output on subsequent calls.

---

### `personal_ai_assistant\api\routes.py`
**Path:** `D:\project\personal_ai_assistant_project\personal_ai_assistant\api\routes.py`

**Purpose:** Added `POST /voice/transcribe` (accepts an audio file upload, returns transcribed text) and `POST /voice/speak` (accepts text, returns a downloadable `.wav` file via `FileResponse`).

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
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class TranscribeResponse(BaseModel):
    text: str


class SpeakRequest(BaseModel):
    text: str


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
```

---

## 5. Errors Faced & How We Solved Them

### Error 1: `curl: (26) Failed to open/read local data from file/application`

**Exact error seen (repeated across multiple attempts):**
```
curl -X POST http://localhost:8000/voice/transcribe -F "file=@data/voice/test_voice.wav"
curl: (26) Failed to open/read local data from file/application
```

**Karanam (Root Cause):** The file `data/voice/test_voice.wav` simply **did not exist** — confirmed repeatedly via `dir data\voice`, which showed `0 File(s)` every time. The plan had been to record a voice memo (e.g. via Windows Voice Recorder) and manually copy it into the `data\voice\` folder, but this manual recording-and-copying step was never actually completed.

**Analogy:** Namma curl-kku "andha file-a upload pண்ணு" nு solрром், aana andha file **existeye illa** — adhான் curl "open pண்ண முடியல" nு solидுchு, repeatedly.

**Fix — a smarter workaround instead of manual recording:** Rather than requiring an actual microphone recording, we used the **already-working `/voice/speak` (TTS) endpoint** to *generate* a `.wav` audio file directly from text, then fed that generated file into `/voice/transcribe` (STT). This self-test loop verifies both directions of the voice pipeline without needing any physical microphone or manual file transfer:
```
curl -X POST http://localhost:8000/voice/speak -H "Content-Type: application/json" -d "{\"text\": \"What is the capital of France\"}" --output data/voice/test_voice.wav

curl -X POST http://localhost:8000/voice/transcribe -F "file=@data/voice/test_voice.wav"
```

**Status:** ✅ Resolved — `dir data\voice` confirmed the file existed (95,706 bytes) after the TTS step, and the subsequent transcription request succeeded, correctly returning `{"text":"What is the capital of France?"}`.

---

## 6. Verified Test Results (Screenshots Confirmed)

### Test: TTS → STT Self-Test Loop

**Step 1 — Generate audio from text (TTS):**
```
curl -X POST http://localhost:8000/voice/speak -H "Content-Type: application/json" -d "{\"text\": \"What is the capital of France\"}" --output data/voice/test_voice.wav
```
Result: `data/voice/test_voice.wav` created (95,706 bytes) — confirmed via `dir data\voice`.

**Step 2 — Transcribe the generated audio back to text (STT):**
```
curl -X POST http://localhost:8000/voice/transcribe -F "file=@data/voice/test_voice.wav"
```
Result:
```json
{"text":"What is the capital of France?"}
```

**Confirmed:** The transcribed text matched the original input almost exactly (Whisper even correctly inferred the question mark from the spoken intonation generated by the TTS engine), proving both the TTS (text → audio) and STT (audio → text) pipelines work correctly end-to-end, fully offline.

---

## 7. Important Notes for Future Reference

- ⚠️ **FFmpeg must be installed as a system-level tool** (not a Python package) before Whisper will work — `winget install "FFmpeg (Essentials Build)"`, verified with `ffmpeg -version` in a fresh CMD window (PATH needs a new window to refresh).
- ⚠️ Always verify a file actually exists (`dir <folder>`) before referencing it in a `curl -F "file=@..."` command — a missing file produces the somewhat cryptic `curl: (26) Failed to open/read local data from file/application` error rather than a clearer "file not found" message.
- The **TTS → STT self-test loop** (generating audio via `/voice/speak` and feeding it into `/voice/transcribe`) is a convenient way to test the voice pipeline without needing an actual microphone or manual file transfers — useful for any future regression testing of this phase.
- Whisper's `base` model (139MB) was used for a balance of speed and accuracy — larger models (`small`, `medium`, `large`) can be swapped in via `whisper_model_size` in `config.py` if transcription accuracy needs improvement for noisier or more complex audio, at the cost of slower processing.
- `pyttsx3` creates a **fresh engine instance on every call** (not a shared global instance) — this is a deliberate choice to avoid known issues where a reused engine can silently stop producing audio output on repeated calls.
- `/voice/transcribe` and `/voice/speak` are currently **standalone** — not yet wired into `/chat`, `/agent/chat`, or `/multiagent/chat`. A full "speak your question, hear the answer" voice loop would require chaining: `/voice/transcribe` → (send text to) `/chat` or `/agent/chat` → (send reply to) `/voice/speak`. This chaining can be done manually today or automated in a future phase/frontend.
- Whisper model files and TTS output `.wav` files are **not currently cleaned up automatically** — `data/voice/` will accumulate files over time; consider adding cleanup logic in a future phase if disk usage becomes a concern.

---

## 8. Next Phase

**Phase 9: Vision + Image Generation** — add image understanding (so the assistant can describe/analyze uploaded images) and image generation via Diffusers, extending the assistant's multimodal capabilities from audio (Phase 8) to visual input and output.

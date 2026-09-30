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
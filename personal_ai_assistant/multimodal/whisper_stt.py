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
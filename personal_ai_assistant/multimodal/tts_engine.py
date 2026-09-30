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

    # A fresh engine instance per call avoids state/threading issues with pyttsx3
    engine = pyttsx3.init()
    engine.setProperty("rate", settings.tts_rate)
    engine.setProperty("volume", settings.tts_volume)
    engine.save_to_file(text, output_path)
    engine.runAndWait()

    logger.info(f"Speech saved to: {output_path}")
    return output_path
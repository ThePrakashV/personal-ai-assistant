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
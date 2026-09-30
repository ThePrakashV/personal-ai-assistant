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
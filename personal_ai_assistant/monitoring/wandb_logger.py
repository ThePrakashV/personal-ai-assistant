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
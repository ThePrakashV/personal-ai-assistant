import os
import threading
from datetime import datetime

from mlflow.tracking import MlflowClient

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

_client = None
_run_id = None
_lock = threading.Lock()
_steps = {}


def _metric_key(path: str) -> str:
    return path.strip("/").replace("/", "_") or "root"


def init_mlflow() -> None:
    """Create one MLflow run for this server session (SQLite backend, no MLflow server needed)."""
    global _client, _run_id
    try:
        os.makedirs(os.path.dirname(settings.mlflow_db_path), exist_ok=True)
        _client = MlflowClient(tracking_uri=f"sqlite:///{settings.mlflow_db_path}")

        experiment = _client.get_experiment_by_name(settings.mlflow_experiment_name)
        experiment_id = (
            experiment.experiment_id
            if experiment
            else _client.create_experiment(settings.mlflow_experiment_name)
        )

        run = _client.create_run(
            experiment_id=experiment_id,
            run_name=f"server-{datetime.now():%Y%m%d-%H%M%S}",
        )
        _run_id = run.info.run_id

        params = {
            "llm_model": settings.ollama_model,
            "vision_model": settings.vision_model,
            "embedding_model": settings.embedding_model_name,
            "whisper_model": settings.whisper_model_size,
            "image_gen_model": settings.image_gen_model,
            "chunk_size": settings.chunk_size,
            "rag_top_k": settings.rag_top_k,
        }
        for key, value in params.items():
            _client.log_param(_run_id, key, value)

        logger.info(f"MLflow tracking started (run_id: {_run_id})")
    except Exception as e:
        _client = None
        logger.error(f"MLflow init failed (server continues without it): {e}")


def log_request(path: str, status_code: int, latency_ms: float) -> None:
    if _client is None or _run_id is None:
        return
    try:
        key = _metric_key(path)
        with _lock:
            step = _steps.get(key, 0)
            _steps[key] = step + 1
        _client.log_metric(_run_id, f"{key}_latency_ms", float(latency_ms), step=step)
        if status_code >= 400:
            _client.log_metric(_run_id, f"{key}_error_status", float(status_code), step=step)
    except Exception as e:
        logger.error(f"MLflow log_request failed: {e}")


def finish_mlflow() -> None:
    if _client is None or _run_id is None:
        return
    try:
        _client.set_terminated(_run_id)
        logger.info("MLflow run finished")
    except Exception as e:
        logger.error(f"MLflow finish failed: {e}")
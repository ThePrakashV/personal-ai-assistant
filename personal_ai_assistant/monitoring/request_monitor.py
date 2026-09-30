import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional

from personal_ai_assistant.monitoring import mlflow_tracker, wandb_logger
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

_lock = threading.Lock()


def init_monitoring() -> None:
    os.makedirs(os.path.dirname(settings.metrics_log_path), exist_ok=True)
    mlflow_tracker.init_mlflow()
    wandb_logger.init_wandb()


def shutdown_monitoring() -> None:
    mlflow_tracker.finish_mlflow()
    wandb_logger.finish_wandb()


def record_request(method: str, path: str, status_code: int, latency_ms: float) -> None:
    """Save one request's metrics to the local JSONL file, MLflow, and W&B."""
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "method": method,
        "path": path,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
    }

    try:
        with _lock:
            with open(settings.metrics_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
    except Exception as e:
        logger.error(f"Failed to write metrics record: {e}")

    mlflow_tracker.log_request(path, status_code, latency_ms)
    wandb_logger.log_request(path, status_code, latency_ms)


def read_records(limit: Optional[int] = None) -> List[Dict]:
    """Read recorded request metrics (most recent `limit` records if given)."""
    if not os.path.exists(settings.metrics_log_path):
        return []

    records: List[Dict] = []
    with _lock:
        with open(settings.metrics_log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return records[-limit:] if limit else records
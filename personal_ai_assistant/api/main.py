import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.concurrency import run_in_threadpool

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger
from personal_ai_assistant.api.routes import router
from personal_ai_assistant.api.websocket import ws_router
from personal_ai_assistant.monitoring.dashboard import dashboard_router
from personal_ai_assistant.monitoring.request_monitor import (
    init_monitoring,
    shutdown_monitoring,
    record_request,
)

logger = get_logger(__name__)

_UNTRACKED_PATHS = ("/dashboard", "/docs", "/openapi.json", "/redoc", "/favicon.ico")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_monitoring()
    yield
    shutdown_monitoring()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    path = request.url.path
    if path.startswith(_UNTRACKED_PATHS):
        return await call_next(request)

    start = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        latency_ms = (time.perf_counter() - start) * 1000
        await run_in_threadpool(record_request, request.method, path, status_code, latency_ms)


app.include_router(router)
app.include_router(ws_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    logger.info("Root endpoint hit")
    return {
        "message": "Personal AI Assistant is running!",
        "app_name": settings.app_name,
        "configured_model": settings.ollama_model,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
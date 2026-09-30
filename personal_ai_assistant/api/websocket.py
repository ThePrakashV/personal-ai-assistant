import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from personal_ai_assistant.llm.inference import generate_response_stream
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    session_id = websocket.query_params.get("session_id") or str(uuid.uuid4())
    logger.info(f"WebSocket client connected — session_id: {session_id}")

    await websocket.send_json({"type": "session", "content": session_id})

    try:
        while True:
            user_message = await websocket.receive_text()

            if not user_message.strip():
                await websocket.send_json({"type": "error", "content": "Message cannot be empty"})
                continue

            logger.info(f"WS received [{session_id}]: {user_message[:50]}...")

            try:
                for chunk in generate_response_stream(session_id, user_message):
                    await websocket.send_json({"type": "chunk", "content": chunk})

                await websocket.send_json({"type": "done"})

            except Exception as e:
                logger.error(f"WS inference failed: {e}")
                await websocket.send_json({"type": "error", "content": "LLM failed to generate a response"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected — session_id: {session_id}")
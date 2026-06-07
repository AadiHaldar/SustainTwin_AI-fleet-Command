"""WebSocket connection manager and telemetry streaming endpoint."""

import logging
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections and provides broadcast capability."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            "WebSocket connected. Active connections: %d",
            len(self.active_connections),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(
            "WebSocket disconnected. Active connections: %d",
            len(self.active_connections),
        )

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        try:
            await websocket.send_json(message)
        except Exception as exc:
            logger.warning("Failed to send personal message: %s", exc)

    async def broadcast(self, message: dict) -> None:
        """Send a JSON message to every connected client."""
        disconnected: List[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up stale connections
        for conn in disconnected:
            self.disconnect(conn)


# Module-level singleton -- imported by telemetry.py
manager = ConnectionManager()


@router.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry streaming."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; we can receive pings or commands
            data = await websocket.receive_text()
            # Echo back as acknowledgement
            await websocket.send_json({"type": "ack", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        logger.warning("WebSocket error: %s", exc)
        manager.disconnect(websocket)

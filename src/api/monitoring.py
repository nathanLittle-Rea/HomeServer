"""API routes for monitoring service."""

import asyncio
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_active_user
from src.models.auth import User
from src.models.monitoring import DashboardMetrics, FileStorageStats, SystemMetrics
from src.services.auth.service import AuthService
from src.services.monitoring import MonitoringService
from src.utils.security import decode_access_token

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

# Initialize services
monitoring_service = MonitoringService(storage_path=settings.storage_path)
auth_service = AuthService()


@router.get("/system", response_model=SystemMetrics)
async def get_system_metrics(
    current_user: User = Depends(get_current_active_user),
) -> SystemMetrics:
    """Get current system metrics.

    Returns:
        SystemMetrics with CPU, memory, and disk usage
    """
    return await monitoring_service.get_system_metrics()


@router.get("/storage", response_model=FileStorageStats)
async def get_storage_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> FileStorageStats:
    """Get file storage statistics.

    Args:
        db: Database session (injected)

    Returns:
        FileStorageStats with file count and total size
    """
    return await monitoring_service.get_file_storage_stats(db)


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardMetrics:
    """Get all dashboard metrics.

    Args:
        db: Database session (injected)

    Returns:
        DashboardMetrics with system and storage stats
    """
    return await monitoring_service.get_dashboard_metrics(db)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None,
) -> None:
    """WebSocket endpoint for real-time metrics updates.

    Args:
        websocket: WebSocket connection
        token: JWT access token for authentication (query parameter)

    Sends dashboard metrics every 2 seconds
    """
    # Authenticate before accepting the connection
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    # Decode and validate token
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    user_id: int = payload.get("user_id")
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    # Verify user exists and is active
    async for db in get_db():
        user = await auth_service.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            await websocket.close(code=4003, reason="User not found or inactive")
            return
        break

    # Accept the connection after successful authentication
    await websocket.accept()

    try:
        # Get database session for this WebSocket connection
        async for db in get_db():
            while True:
                try:
                    # Get latest metrics
                    metrics = await monitoring_service.get_dashboard_metrics(db)

                    # Send to client
                    await websocket.send_json(metrics.model_dump(mode="json"))

                    # Wait 2 seconds before next update
                    await asyncio.sleep(2)

                except WebSocketDisconnect:
                    break
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    break

            # Break outer loop when websocket disconnects
            break

    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

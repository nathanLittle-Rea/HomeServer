"""API routes for monitoring service."""

import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.monitoring import DashboardMetrics, FileStorageStats, SystemMetrics
from src.services.monitoring import MonitoringService

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

# Initialize monitoring service
monitoring_service = MonitoringService(storage_path=settings.storage_path)


@router.get("/system", response_model=SystemMetrics)
async def get_system_metrics() -> SystemMetrics:
    """Get current system metrics.

    Returns:
        SystemMetrics with CPU, memory, and disk usage
    """
    return await monitoring_service.get_system_metrics()


@router.get("/storage", response_model=FileStorageStats)
async def get_storage_stats(db: AsyncSession = Depends(get_db)) -> FileStorageStats:
    """Get file storage statistics.

    Args:
        db: Database session (injected)

    Returns:
        FileStorageStats with file count and total size
    """
    return await monitoring_service.get_file_storage_stats(db)


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
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
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time metrics updates.

    Args:
        websocket: WebSocket connection

    Sends dashboard metrics every 2 seconds
    """
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

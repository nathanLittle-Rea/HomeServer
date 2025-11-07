"""Monitoring service implementation."""

import time
from pathlib import Path

import psutil
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.db_models import FileMetadataDB
from src.models.monitoring import DashboardMetrics, FileStorageStats, SystemMetrics

# Track server start time
SERVER_START_TIME = time.time()


class MonitoringService:
    """Service for collecting system and application metrics."""

    def __init__(self, storage_path: str = "./storage") -> None:
        """Initialize the monitoring service.

        Args:
            storage_path: Directory where files are stored
        """
        self.storage_path = Path(storage_path)

    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system resource metrics.

        Returns:
            SystemMetrics object with current system stats
        """
        # CPU usage (percentage)
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)

        # Disk usage for storage path
        disk = psutil.disk_usage(str(self.storage_path))
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        disk_free_gb = disk.free / (1024**3)

        return SystemMetrics(
            cpu_percent=round(cpu_percent, 1),
            memory_percent=round(memory.percent, 1),
            memory_used_gb=round(memory_used_gb, 2),
            memory_total_gb=round(memory_total_gb, 2),
            disk_percent=round(disk.percent, 1),
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            disk_free_gb=round(disk_free_gb, 2),
        )

    async def get_file_storage_stats(self, db: AsyncSession) -> FileStorageStats:
        """Get file storage statistics from database.

        Args:
            db: Database session

        Returns:
            FileStorageStats object with storage statistics
        """
        # Count total files
        count_result = await db.execute(select(func.count(FileMetadataDB.id)))
        total_files = count_result.scalar() or 0

        # Sum total size
        size_result = await db.execute(select(func.sum(FileMetadataDB.size)))
        total_size_bytes = size_result.scalar() or 0
        total_size_gb = total_size_bytes / (1024**3)

        return FileStorageStats(
            total_files=total_files,
            total_size_gb=round(total_size_gb, 4),
            storage_path=str(self.storage_path),
        )

    async def get_dashboard_metrics(self, db: AsyncSession) -> DashboardMetrics:
        """Get all dashboard metrics.

        Args:
            db: Database session

        Returns:
            DashboardMetrics object with all metrics
        """
        system_metrics = await self.get_system_metrics()
        storage_stats = await self.get_file_storage_stats(db)
        uptime = time.time() - SERVER_START_TIME

        return DashboardMetrics(
            system=system_metrics,
            storage=storage_stats,
            uptime_seconds=round(uptime, 1),
        )

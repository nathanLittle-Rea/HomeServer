"""Data models for monitoring service."""

from typing import Optional

from pydantic import BaseModel, Field


class SystemMetrics(BaseModel):
    """System resource metrics."""

    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_used_gb: float = Field(..., description="Memory used in GB")
    memory_total_gb: float = Field(..., description="Total memory in GB")
    disk_percent: float = Field(..., description="Disk usage percentage")
    disk_used_gb: float = Field(..., description="Disk used in GB")
    disk_total_gb: float = Field(..., description="Total disk space in GB")
    disk_free_gb: float = Field(..., description="Free disk space in GB")


class FileStorageStats(BaseModel):
    """File storage statistics."""

    total_files: int = Field(..., description="Total number of files")
    total_size_gb: float = Field(..., description="Total size of all files in GB")
    storage_path: str = Field(..., description="Path where files are stored")


class DashboardMetrics(BaseModel):
    """Combined dashboard metrics."""

    system: SystemMetrics
    storage: FileStorageStats
    uptime_seconds: float = Field(..., description="Server uptime in seconds")

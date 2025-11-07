"""Pydantic models for file browser."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FileSystemItem(BaseModel):
    """Represents a file or directory in the file system."""

    name: str = Field(..., description="File or directory name")
    path: str = Field(..., description="Absolute path")
    is_directory: bool = Field(..., description="True if directory, False if file")
    size: Optional[int] = Field(None, description="File size in bytes (None for directories)")
    modified: Optional[datetime] = Field(None, description="Last modified timestamp")
    permissions: Optional[str] = Field(None, description="File permissions (e.g., 'rwxr-xr-x')")
    is_readable: bool = Field(default=True, description="Whether item is readable")


class DirectoryListing(BaseModel):
    """Response model for directory listing."""

    path: str = Field(..., description="Current directory path")
    parent: Optional[str] = Field(None, description="Parent directory path")
    items: list[FileSystemItem] = Field(..., description="Files and directories")
    total_items: int = Field(..., description="Total number of items")


class DownloadRequest(BaseModel):
    """Request model for downloading a file from file system."""

    path: str = Field(..., description="Absolute path to file")

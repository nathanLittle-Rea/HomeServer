"""Data models for file storage service."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """Metadata for a stored file."""

    id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    size: int = Field(..., description="File size in bytes")
    upload_date: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    tags: list[str] = Field(default_factory=list, description="User-defined tags")


class FileUploadResponse(BaseModel):
    """Response after successful file upload."""

    id: str
    filename: str
    size: int
    message: str = "File uploaded successfully"


class FileListResponse(BaseModel):
    """Response for file listing."""

    files: list[FileMetadata]
    total: int


class FileDeleteResponse(BaseModel):
    """Response after file deletion."""

    id: str
    message: str = "File deleted successfully"

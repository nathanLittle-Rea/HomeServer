"""API routes for file storage service."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.files import (
    FileDeleteResponse,
    FileListResponse,
    FileMetadata,
    FileUploadResponse,
)
from src.services.files import FileStorageService

# Create router
router = APIRouter(prefix="/api/v1/files", tags=["files"])

# Initialize file storage service with configured path
file_service = FileStorageService(storage_path=settings.storage_path)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
) -> FileUploadResponse:
    """Upload a file to the storage service.

    Args:
        file: The file to upload
        tags: Optional comma-separated tags
        db: Database session (injected)

    Returns:
        FileUploadResponse with file details
    """
    # Read file content
    content = await file.read()

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Save file
    metadata = await file_service.save_file(
        db=db,
        file_content=content,
        filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        tags=tag_list,
    )

    return FileUploadResponse(
        id=metadata.id,
        filename=metadata.filename,
        size=metadata.size,
    )


@router.get("/list", response_model=FileListResponse)
async def list_files(
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> FileListResponse:
    """List all files, optionally filtered by tag.

    Args:
        tag: Optional tag to filter by
        db: Database session (injected)

    Returns:
        FileListResponse with list of files
    """
    files = await file_service.list_files(db=db, tag=tag)

    return FileListResponse(
        files=files,
        total=len(files),
    )


@router.get("/{file_id}/metadata", response_model=FileMetadata)
async def get_file_metadata(
    file_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileMetadata:
    """Get metadata for a specific file.

    Args:
        file_id: The unique file identifier
        db: Database session (injected)

    Returns:
        FileMetadata object

    Raises:
        HTTPException: If file not found
    """
    metadata = await file_service.get_metadata(db=db, file_id=file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")

    return metadata


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Download a file.

    Args:
        file_id: The unique file identifier
        db: Database session (injected)

    Returns:
        StreamingResponse with file content

    Raises:
        HTTPException: If file not found
    """
    try:
        content, metadata = await file_service.get_file(db=db, file_id=file_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    # Create streaming response
    return StreamingResponse(
        iter([content]),
        media_type=metadata.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{metadata.filename}"'
        },
    )


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileDeleteResponse:
    """Delete a file.

    Args:
        file_id: The unique file identifier
        db: Database session (injected)

    Returns:
        FileDeleteResponse confirming deletion

    Raises:
        HTTPException: If file not found
    """
    try:
        await file_service.delete_file(db=db, file_id=file_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    return FileDeleteResponse(id=file_id)

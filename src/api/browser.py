"""API routes for file browser service."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.config import settings
from src.models.browser import DirectoryListing, FileSystemItem
from src.services.browser import FileBrowserService

# Create router
router = APIRouter(prefix="/api/v1/browser", tags=["browser"])

# Initialize file browser service with allowed paths
# Allow browsing: external drive, user home directory, and /tmp
allowed_paths = [
    "/Volumes/allDaStuffs",
    str(settings.storage_path),
]

file_browser = FileBrowserService(allowed_paths=allowed_paths)


@router.get("/list", response_model=DirectoryListing)
async def list_directory(
    path: str = Query(..., description="Directory path to list"),
) -> DirectoryListing:
    """List contents of a directory.

    Args:
        path: Directory path to list

    Returns:
        DirectoryListing with files and subdirectories

    Raises:
        HTTPException: 403 if access denied, 404 if not found, 400 if not a directory
    """
    try:
        return await file_browser.list_directory(path)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing directory: {str(e)}")


@router.get("/info", response_model=FileSystemItem)
async def get_file_info(
    path: str = Query(..., description="File or directory path"),
) -> FileSystemItem:
    """Get metadata for a file or directory.

    Args:
        path: File or directory path

    Returns:
        FileSystemItem with metadata

    Raises:
        HTTPException: 403 if access denied, 404 if not found
    """
    try:
        return await file_browser.get_file_info(path)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")


@router.get("/download")
async def download_file(
    path: str = Query(..., description="File path to download"),
) -> StreamingResponse:
    """Download a file from the file system.

    Args:
        path: File path to download

    Returns:
        StreamingResponse with file content

    Raises:
        HTTPException: 403 if access denied, 404 if not found, 400 if path is a directory
    """
    try:
        content, metadata = await file_browser.get_file(path)

        # Create streaming response
        return StreamingResponse(
            iter([content]),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{metadata.name}"'
            },
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IsADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@router.get("/roots", response_model=list[str])
async def get_root_paths() -> list[str]:
    """Get list of allowed root paths for browsing.

    Returns:
        List of allowed root directory paths
    """
    return allowed_paths

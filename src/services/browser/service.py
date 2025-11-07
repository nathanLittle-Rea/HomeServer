"""File browser service implementation."""

import os
import stat
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiofiles

from src.models.browser import DirectoryListing, FileSystemItem


class FileBrowserService:
    """Service for browsing the file system."""

    def __init__(self, allowed_paths: Optional[list[str]] = None) -> None:
        """Initialize the file browser service.

        Args:
            allowed_paths: List of allowed root paths to browse. If None, allows all paths.
        """
        self.allowed_paths = allowed_paths or []

    def _is_path_allowed(self, path: Path) -> bool:
        """Check if a path is within allowed paths.

        Args:
            path: Path to check

        Returns:
            True if path is allowed, False otherwise
        """
        if not self.allowed_paths:
            # If no restrictions, allow all paths
            return True

        path_str = str(path.resolve())
        return any(path_str.startswith(allowed) for allowed in self.allowed_paths)

    def _get_file_permissions(self, path: Path) -> str:
        """Get file permissions in rwx format.

        Args:
            path: Path to file

        Returns:
            Permission string (e.g., 'rwxr-xr-x')
        """
        try:
            st = path.stat()
            mode = st.st_mode

            # Owner permissions
            owner = ""
            owner += "r" if mode & stat.S_IRUSR else "-"
            owner += "w" if mode & stat.S_IWUSR else "-"
            owner += "x" if mode & stat.S_IXUSR else "-"

            # Group permissions
            group = ""
            group += "r" if mode & stat.S_IRGRP else "-"
            group += "w" if mode & stat.S_IWGRP else "-"
            group += "x" if mode & stat.S_IXGRP else "-"

            # Other permissions
            other = ""
            other += "r" if mode & stat.S_IROTH else "-"
            other += "w" if mode & stat.S_IWOTH else "-"
            other += "x" if mode & stat.S_IXOTH else "-"

            return f"{owner}{group}{other}"
        except Exception:
            return "?"

    async def list_directory(self, path: str) -> DirectoryListing:
        """List contents of a directory.

        Args:
            path: Directory path to list

        Returns:
            DirectoryListing with files and subdirectories

        Raises:
            PermissionError: If path is not allowed
            FileNotFoundError: If directory doesn't exist
            NotADirectoryError: If path is not a directory
        """
        dir_path = Path(path).resolve()

        # Check if path is allowed
        if not self._is_path_allowed(dir_path):
            raise PermissionError(f"Access to {path} is not allowed")

        # Check if path exists and is a directory
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory {path} not found")

        if not dir_path.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")

        # Get parent directory
        parent = str(dir_path.parent) if dir_path.parent != dir_path else None

        # List directory contents
        items: list[FileSystemItem] = []

        try:
            for entry in dir_path.iterdir():
                try:
                    # Get file stats
                    stats = entry.stat()
                    is_dir = entry.is_dir()

                    # Create FileSystemItem
                    item = FileSystemItem(
                        name=entry.name,
                        path=str(entry),
                        is_directory=is_dir,
                        size=None if is_dir else stats.st_size,
                        modified=datetime.fromtimestamp(stats.st_mtime),
                        permissions=self._get_file_permissions(entry),
                        is_readable=os.access(entry, os.R_OK),
                    )
                    items.append(item)
                except (PermissionError, OSError):
                    # Skip items we can't access
                    continue

            # Sort: directories first, then by name
            items.sort(key=lambda x: (not x.is_directory, x.name.lower()))

        except PermissionError:
            raise PermissionError(f"Permission denied to read {path}")

        return DirectoryListing(
            path=str(dir_path),
            parent=parent,
            items=items,
            total_items=len(items),
        )

    async def get_file(self, path: str) -> tuple[bytes, FileSystemItem]:
        """Get a file's content and metadata.

        Args:
            path: File path

        Returns:
            Tuple of (file_content, metadata)

        Raises:
            PermissionError: If path is not allowed
            FileNotFoundError: If file doesn't exist
            IsADirectoryError: If path is a directory
        """
        file_path = Path(path).resolve()

        # Check if path is allowed
        if not self._is_path_allowed(file_path):
            raise PermissionError(f"Access to {path} is not allowed")

        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File {path} not found")

        # Check if it's a file
        if file_path.is_dir():
            raise IsADirectoryError(f"{path} is a directory")

        # Read file
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        # Get metadata
        stats = file_path.stat()
        metadata = FileSystemItem(
            name=file_path.name,
            path=str(file_path),
            is_directory=False,
            size=stats.st_size,
            modified=datetime.fromtimestamp(stats.st_mtime),
            permissions=self._get_file_permissions(file_path),
            is_readable=True,
        )

        return content, metadata

    async def get_file_info(self, path: str) -> FileSystemItem:
        """Get metadata for a file or directory.

        Args:
            path: File or directory path

        Returns:
            FileSystemItem with metadata

        Raises:
            PermissionError: If path is not allowed
            FileNotFoundError: If file doesn't exist
        """
        item_path = Path(path).resolve()

        # Check if path is allowed
        if not self._is_path_allowed(item_path):
            raise PermissionError(f"Access to {path} is not allowed")

        # Check if path exists
        if not item_path.exists():
            raise FileNotFoundError(f"{path} not found")

        # Get metadata
        stats = item_path.stat()
        is_dir = item_path.is_dir()

        return FileSystemItem(
            name=item_path.name,
            path=str(item_path),
            is_directory=is_dir,
            size=None if is_dir else stats.st_size,
            modified=datetime.fromtimestamp(stats.st_mtime),
            permissions=self._get_file_permissions(item_path),
            is_readable=os.access(item_path, os.R_OK),
        )

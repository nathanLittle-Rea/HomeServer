"""File storage service implementation with PostgreSQL."""

import uuid
from pathlib import Path
from typing import Optional

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.db_models import FileMetadataDB
from src.models.files import FileMetadata


class FileStorageService:
    """Service for managing file storage operations."""

    def __init__(self, storage_path: str = "./storage") -> None:
        """Initialize the file storage service.

        Args:
            storage_path: Directory where files will be stored
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        db: AsyncSession,
        file_content: bytes,
        filename: str,
        content_type: str,
        tags: Optional[list[str]] = None,
    ) -> FileMetadata:
        """Save a file and its metadata to storage and database.

        Args:
            db: Database session
            file_content: The file content as bytes
            filename: Original filename
            content_type: MIME type of the file
            tags: Optional list of tags

        Returns:
            FileMetadata object for the saved file
        """
        # Generate unique ID
        file_id = str(uuid.uuid4())
        file_path = self.storage_path / file_id

        # Save file to disk
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        # Create database record
        db_metadata = FileMetadataDB(
            id=file_id,
            filename=filename,
            content_type=content_type,
            size=len(file_content),
            tags=tags or [],
        )

        db.add(db_metadata)
        await db.flush()
        await db.refresh(db_metadata)

        # Convert to Pydantic model
        return self._db_to_pydantic(db_metadata)

    async def get_file(
        self, db: AsyncSession, file_id: str
    ) -> tuple[bytes, FileMetadata]:
        """Retrieve a file and its metadata.

        Args:
            db: Database session
            file_id: The unique file identifier

        Returns:
            Tuple of (file_content, metadata)

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        # Get metadata from database
        result = await db.execute(
            select(FileMetadataDB).where(FileMetadataDB.id == file_id)
        )
        db_metadata = result.scalar_one_or_none()

        if not db_metadata:
            raise FileNotFoundError(f"File with ID {file_id} not found")

        # Read file from disk
        file_path = self.storage_path / file_id
        if not file_path.exists():
            raise FileNotFoundError(f"File with ID {file_id} not found on disk")

        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        return content, self._db_to_pydantic(db_metadata)

    async def list_files(
        self, db: AsyncSession, tag: Optional[str] = None
    ) -> list[FileMetadata]:
        """List all files, optionally filtered by tag.

        Args:
            db: Database session
            tag: Optional tag to filter by

        Returns:
            List of FileMetadata objects
        """
        query = select(FileMetadataDB)

        if tag:
            # Filter by tag using PostgreSQL array contains operator
            query = query.where(FileMetadataDB.tags.any(tag))

        # Order by upload date, newest first
        query = query.order_by(FileMetadataDB.upload_date.desc())

        result = await db.execute(query)
        db_files = result.scalars().all()

        return [self._db_to_pydantic(f) for f in db_files]

    async def delete_file(self, db: AsyncSession, file_id: str) -> None:
        """Delete a file and its metadata.

        Args:
            db: Database session
            file_id: The unique file identifier

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        # Get metadata from database
        result = await db.execute(
            select(FileMetadataDB).where(FileMetadataDB.id == file_id)
        )
        db_metadata = result.scalar_one_or_none()

        if not db_metadata:
            raise FileNotFoundError(f"File with ID {file_id} not found")

        # Delete file from disk
        file_path = self.storage_path / file_id
        if file_path.exists():
            file_path.unlink()

        # Delete from database
        await db.delete(db_metadata)

    async def get_metadata(
        self, db: AsyncSession, file_id: str
    ) -> Optional[FileMetadata]:
        """Get metadata for a file without reading the file content.

        Args:
            db: Database session
            file_id: The unique file identifier

        Returns:
            FileMetadata or None if not found
        """
        result = await db.execute(
            select(FileMetadataDB).where(FileMetadataDB.id == file_id)
        )
        db_metadata = result.scalar_one_or_none()

        if not db_metadata:
            return None

        return self._db_to_pydantic(db_metadata)

    @staticmethod
    def _db_to_pydantic(db_model: FileMetadataDB) -> FileMetadata:
        """Convert database model to Pydantic model.

        Args:
            db_model: Database model instance

        Returns:
            Pydantic FileMetadata model
        """
        return FileMetadata(
            id=db_model.id,
            filename=db_model.filename,
            content_type=db_model.content_type,
            size=db_model.size,
            upload_date=db_model.upload_date,
            tags=db_model.tags,
        )

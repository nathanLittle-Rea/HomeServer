"""SQLAlchemy database models."""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.database import Base


class FileMetadataDB(Base):
    """Database model for file metadata."""

    __tablename__ = "file_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=list)

    def __repr__(self) -> str:
        """String representation of file metadata."""
        return f"<FileMetadata(id={self.id}, filename={self.filename})>"

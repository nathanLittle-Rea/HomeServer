"""Database initialization script."""

import asyncio

from src.database import Base, engine
from src.models.db_models import FileMetadataDB  # noqa: F401 - Import to register model


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())

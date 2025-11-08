"""Authentication service implementation."""

from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import User, UserCreate, UserUpdate
from src.models.db_models import UserDB
from src.utils.security import get_password_hash, verify_password


class AuthService:
    """Service for user authentication and management."""

    async def create_user(self, db: AsyncSession, user_create: UserCreate) -> User:
        """Create a new user.

        Args:
            db: Database session
            user_create: User creation data

        Returns:
            Created user

        Raises:
            ValueError: If username or email already exists
        """
        # Check if username already exists
        result = await db.execute(
            select(UserDB).where(UserDB.username == user_create.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")

        # Check if email already exists
        result = await db.execute(
            select(UserDB).where(UserDB.email == user_create.email)
        )
        if result.scalar_one_or_none():
            raise ValueError("Email already exists")

        # Create user
        db_user = UserDB(
            username=user_create.username,
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
        )

        db.add(db_user)
        await db.flush()
        await db.refresh(db_user)

        return User.model_validate(db_user)

    async def authenticate_user(
        self, db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        """Authenticate a user by username/email and password.

        Args:
            db: Database session
            username: Username or email
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        # Find user by username or email
        result = await db.execute(
            select(UserDB).where(
                or_(UserDB.username == username, UserDB.email == username)
            )
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        if not verify_password(password, db_user.hashed_password):
            return None

        if not db_user.is_active:
            return None

        return User.model_validate(db_user)

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        result = await db.execute(select(UserDB).where(UserDB.id == user_id))
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        return User.model_validate(db_user)

    async def get_user_by_username(
        self, db: AsyncSession, username: str
    ) -> Optional[User]:
        """Get user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User if found, None otherwise
        """
        result = await db.execute(
            select(UserDB).where(UserDB.username == username)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        return User.model_validate(db_user)

    async def update_user(
        self, db: AsyncSession, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        """Update user information.

        Args:
            db: Database session
            user_id: User ID
            user_update: Update data

        Returns:
            Updated user, or None if not found

        Raises:
            ValueError: If email already exists (for another user)
        """
        result = await db.execute(select(UserDB).where(UserDB.id == user_id))
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        # Check if email is being updated and already exists
        if user_update.email and user_update.email != db_user.email:
            result = await db.execute(
                select(UserDB).where(
                    UserDB.email == user_update.email, UserDB.id != user_id
                )
            )
            if result.scalar_one_or_none():
                raise ValueError("Email already exists")

            db_user.email = user_update.email

        # Update password if provided
        if user_update.password:
            db_user.hashed_password = get_password_hash(user_update.password)

        await db.flush()
        await db.refresh(db_user)

        return User.model_validate(db_user)

    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        """Delete a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(select(UserDB).where(UserDB.id == user_id))
        db_user = result.scalar_one_or_none()

        if not db_user:
            return False

        await db.delete(db_user)
        return True

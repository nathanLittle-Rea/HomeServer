"""API routes for authentication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_active_user, get_current_superuser
from src.models.auth import LoginRequest, RegisterResponse, Token, User, UserCreate, UserUpdate
from src.services.auth import AuthService
from src.utils.security import create_access_token

# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# Initialize auth service
auth_service = AuthService()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """Register a new user.

    Args:
        user_create: User registration data
        db: Database session

    Returns:
        RegisterResponse with user and access token

    Raises:
        HTTPException: 400 if username or email already exists
    """
    try:
        # Create user
        user = await auth_service.create_user(db, user_create)

        # Create access token
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )

        return RegisterResponse(
            user=user,
            access_token=access_token,
            token_type="bearer"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Login and get access token.

    Args:
        login_request: Login credentials
        db: Database session

    Returns:
        Token with access token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Authenticate user
    user = await auth_service.authenticate_user(
        db, login_request.username, login_request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user
    """
    return current_user


@router.patch("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update current user information.

    Args:
        user_update: Update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user

    Raises:
        HTTPException: 400 if email already exists
    """
    try:
        updated_user = await auth_service.update_user(db, current_user.id, user_update)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return updated_user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete current user account.

    Args:
        current_user: Current authenticated user
        db: Database session
    """
    await auth_service.delete_user(db, current_user.id)


@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get user by ID (superuser only).

    Args:
        user_id: User ID
        current_user: Current authenticated superuser
        db: Database session

    Returns:
        User

    Raises:
        HTTPException: 404 if user not found
    """
    user = await auth_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

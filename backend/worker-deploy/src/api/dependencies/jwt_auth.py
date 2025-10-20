"""
TranslateCloud - JWT Authentication Dependency
Validates JWT tokens created by the local auth system
"""

from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from src.config.settings import settings

security = HTTPBearer()

# JWT settings (must match auth.py)
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Validate JWT token and extract user information

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        dict with user_id and email

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Extract user_id - try both locations for compatibility
        user_id: str = payload.get("user_id") or payload.get("sub")
        email: str = payload.get("sub")  # sub contains email in our tokens

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": user_id,
            "email": email
        }

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    current_user: dict = Depends(get_current_user)
) -> str:
    """
    Extract just the user_id from current user

    Args:
        current_user: User dict from get_current_user

    Returns:
        user_id string
    """
    return current_user["user_id"]

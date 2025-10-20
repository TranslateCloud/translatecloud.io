from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests
from functools import lru_cache
from src.config.settings import settings

security = HTTPBearer()

@lru_cache()
def get_cognito_public_keys():
    keys_url = f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    response = requests.get(keys_url)
    return response.json()

def verify_cognito_token(token: str) -> dict:
    try:
        keys = get_cognito_public_keys()
        headers = jwt.get_unverified_headers(token)
        kid = headers["kid"]

        key = next((k for k in keys["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key"
            )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.COGNITO_CLIENT_ID,
            issuer=f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}"
        )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    payload = verify_cognito_token(token)
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "cognito_username": payload.get("cognito:username")
    }

async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> str:
    """
    Extract just the user_id from current user

    Args:
        current_user: User dict from get_current_user

    Returns:
        user_id string
    """
    return current_user["user_id"]
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from src.config.database import get_db
from src.schemas.user import UserCreate, UserResponse
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import uuid
import os

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user: UserCreate,
    cursor: RealDictCursor = Depends(get_db)
):
    # Check if user exists
    cursor.execute(
        "SELECT id FROM users WHERE email = %s",
        (user.email,)
    )
    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    # Hash password
    hashed_password = pwd_context.hash(user.password)

    # Create full name
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or None

    user_id = str(uuid.uuid4())

    # Insert user
    cursor.execute(
        '''
        INSERT INTO users
        (id, email, password_hash, full_name, plan, subscription_status, words_used_this_month, word_limit, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        RETURNING id, email, full_name, plan, subscription_status, words_used_this_month, word_limit, created_at
        ''',
        (
            user_id,
            user.email,
            hashed_password,
            full_name,
            'free',
            'active',
            0,
            5000
        )
    )

    new_user = cursor.fetchone()

    # Create access token
    access_token = create_access_token(data={"sub": user.email, "user_id": user_id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(new_user['id']),
            "email": new_user['email'],
            "full_name": new_user['full_name'],
            "plan": new_user['plan'],
            "subscription_status": new_user['subscription_status'],
            "words_used_this_month": new_user['words_used_this_month'],
            "word_limit": new_user['word_limit']
        }
    }

@router.post("/login")
async def login(
    email: str,
    password: str,
    cursor: RealDictCursor = Depends(get_db)
):
    # Get user
    cursor.execute(
        "SELECT id, email, password_hash, full_name, plan, subscription_status, words_used_this_month, word_limit FROM users WHERE email = %s",
        (email,)
    )
    user = cursor.fetchone()

    if not user or not pwd_context.verify(password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token = create_access_token(data={"sub": user['email'], "user_id": str(user['id'])})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user['id']),
            "email": user['email'],
            "full_name": user['full_name'],
            "plan": user['plan'],
            "subscription_status": user['subscription_status'],
            "words_used_this_month": user['words_used_this_month'],
            "word_limit": user['word_limit']
        }
    }

@router.get("/me")
async def get_current_user():
    return {
        "message": "Get current user - JWT authentication pending",
        "status": "not_implemented"
    }

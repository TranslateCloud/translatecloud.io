from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from src.config.database import get_db
from src.schemas.user import UserCreate, UserResponse
import uuid

router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user: UserCreate,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "SELECT id FROM users WHERE email = %s OR cognito_sub = %s",
        (user.email, user.cognito_sub)
    )
    existing_user = cursor.fetchone()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    user_id = str(uuid.uuid4())
    
    cursor.execute(
        '''
        INSERT INTO users 
        (id, email, cognito_sub, full_name, company, plan, subscription_status, monthly_word_count, word_limit)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        ''',
        (
            user_id,
            user.email,
            user.cognito_sub,
            user.full_name,
            user.company,
            'free',
            'active',
            0,
            5000
        )
    )
    
    new_user = cursor.fetchone()
    return new_user

@router.post("/login")
async def login():
    return {
        "message": "Login endpoint - Cognito integration pending",
        "status": "not_implemented"
    }

@router.get("/me")
async def get_current_user():
    return {
        "message": "Get current user - JWT authentication pending",
        "status": "not_implemented"
    }
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from src.config.database import get_db
from src.schemas.user import UserResponse, UserUpdate
from typing import Dict

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_id: str,
    user_update: UserUpdate,
    cursor: RealDictCursor = Depends(get_db)
):
    update_data = user_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(user_id)
    
    cursor.execute(
        f"UPDATE users SET {set_clause} WHERE id = %s RETURNING *",
        values
    )
    
    updated_user = cursor.fetchone()
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.get("/stats")
async def get_user_stats(
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        '''
        SELECT 
            u.monthly_word_count,
            u.word_limit,
            COUNT(DISTINCT p.id) as total_projects,
            COUNT(t.id) as total_translations,
            COALESCE(SUM(t.word_count), 0) as total_words_translated
        FROM users u
        LEFT JOIN projects p ON u.id = p.user_id
        LEFT JOIN translations t ON p.id = t.project_id
        WHERE u.id = %s
        GROUP BY u.id, u.monthly_word_count, u.word_limit
        ''',
        (user_id,)
    )
    
    stats = cursor.fetchone()
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return stats
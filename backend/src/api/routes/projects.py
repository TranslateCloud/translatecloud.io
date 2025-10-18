from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from src.config.database import get_db
from src.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from typing import List
import uuid

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    projects = cursor.fetchall()
    return projects

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    user_id: str,
    project: ProjectCreate,
    cursor: RealDictCursor = Depends(get_db)
):
    project_id = str(uuid.uuid4())
    
    cursor.execute(
        '''
        INSERT INTO projects (id, user_id, name, url, source_lang, target_lang, status, total_words, translated_words)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        ''',
        (
            project_id,
            user_id,
            project.name,
            str(project.url) if project.url else None,
            project.source_lang,
            project.target_lang,
            'pending',
            0,
            0
        )
    )
    
    new_project = cursor.fetchone()
    return new_project

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "SELECT * FROM projects WHERE id = %s AND user_id = %s",
        (project_id, user_id)
    )
    project = cursor.fetchone()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    user_id: str,
    project_update: ProjectUpdate,
    cursor: RealDictCursor = Depends(get_db)
):
    update_data = project_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.extend([project_id, user_id])
    
    cursor.execute(
        f"UPDATE projects SET {set_clause} WHERE id = %s AND user_id = %s RETURNING *",
        values
    )
    
    updated_project = cursor.fetchone()
    
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "DELETE FROM projects WHERE id = %s AND user_id = %s RETURNING id",
        (project_id, user_id)
    )
    
    deleted = cursor.fetchone()
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return None
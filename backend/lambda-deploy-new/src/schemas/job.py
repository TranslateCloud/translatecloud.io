"""
Translation Job Schemas

Pydantic models for async translation job management.
Used for DynamoDB storage and API request/response validation.

Author: TranslateCloud Team
Last Updated: 2025-10-20
"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobSubmitRequest(BaseModel):
    """
    Request schema for submitting a new translation job

    Used by: POST /api/jobs/translate
    """
    url: HttpUrl = Field(..., description="Website URL to translate")
    source_lang: str = Field(..., min_length=2, max_length=5, description="Source language code (e.g., 'en', 'es')")
    target_lang: str = Field(..., min_length=2, max_length=5, description="Target language code (e.g., 'en', 'es')")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "source_lang": "en",
                "target_lang": "es"
            }
        }


class JobSubmitResponse(BaseModel):
    """
    Response schema after submitting a job

    Returned by: POST /api/jobs/translate
    """
    job_id: str = Field(..., description="Unique job identifier (UUID)")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Human-readable status message")
    poll_url: str = Field(..., description="URL to poll for job status")
    created_at: datetime = Field(..., description="Job creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending",
                "message": "Translation job created. Use job_id to check progress.",
                "poll_url": "/api/jobs/550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2025-10-20T15:30:00Z"
            }
        }


class JobStatusResponse(BaseModel):
    """
    Response schema for job status queries

    Returned by: GET /api/jobs/{job_id}
    """
    job_id: str
    user_id: str
    status: JobStatus
    url: str
    source_lang: str
    target_lang: str
    progress: int = Field(0, ge=0, le=100, description="Progress percentage (0-100)")
    pages_total: Optional[int] = None
    pages_translated: Optional[int] = None
    words_total: Optional[int] = None
    words_translated: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None
    result_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user123",
                "status": "processing",
                "url": "https://example.com",
                "source_lang": "en",
                "target_lang": "es",
                "progress": 65,
                "pages_total": 10,
                "pages_translated": 7,
                "words_total": 5000,
                "words_translated": 3500,
                "created_at": "2025-10-20T15:30:00Z",
                "started_at": "2025-10-20T15:30:05Z",
                "message": "Translating page 7 of 10..."
            }
        }


class JobListResponse(BaseModel):
    """
    Response schema for listing user's jobs

    Returned by: GET /api/jobs
    """
    jobs: list[JobStatusResponse]
    total: int
    page: int
    page_size: int

    class Config:
        json_schema_extra = {
            "example": {
                "jobs": [
                    {
                        "job_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "completed",
                        "url": "https://example.com",
                        "progress": 100,
                        "created_at": "2025-10-20T15:30:00Z",
                        "completed_at": "2025-10-20T15:35:20Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20
            }
        }


class DynamoDBJob(BaseModel):
    """
    Complete job model for DynamoDB storage

    All fields match DynamoDB table schema
    """
    job_id: str
    user_id: str
    status: JobStatus
    url: str
    source_lang: str
    target_lang: str
    progress: int = 0
    pages_total: Optional[int] = None
    pages_translated: Optional[int] = None
    words_total: Optional[int] = None
    words_translated: Optional[int] = None
    created_at: str  # ISO format string for DynamoDB
    updated_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    result_url: Optional[str] = None
    download_url: Optional[str] = None
    ttl: int  # Unix timestamp for auto-deletion (7 days)

    class Config:
        use_enum_values = True  # Store enum as string in DynamoDB

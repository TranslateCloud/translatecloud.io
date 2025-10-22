"""
Jobs API Routes - Async Translation Job Management

Endpoints for submitting, tracking, and managing translation jobs.

Endpoints:
- POST /api/jobs/translate - Submit new translation job
- GET /api/jobs/{job_id} - Get job status
- GET /api/jobs - List user's jobs
- DELETE /api/jobs/{job_id} - Cancel job

Author: TranslateCloud Team
Last Updated: 2025-10-20
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from src.schemas.job import (
    JobSubmitRequest,
    JobSubmitResponse,
    JobStatusResponse,
    JobListResponse,
    JobStatus
)
from src.core.job_manager import (
    create_job,
    get_job,
    get_user_jobs,
    delete_job
)
from src.api.dependencies.jwt_auth import get_current_user_id

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/translate", response_model=JobSubmitResponse, status_code=202)
async def submit_translation_job(
    request: JobSubmitRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Submit a new translation job (async processing)

    **Flow:**
    1. Creates job in DynamoDB with status "pending"
    2. Sends message to SQS queue for background processing
    3. Returns job_id immediately (< 1 second)
    4. Client polls GET /api/jobs/{job_id} for progress

    **Returns:**
    - HTTP 202 Accepted (job queued, not completed yet)
    - job_id for tracking progress

    **Example:**
    ```bash
    curl -X POST /api/jobs/translate \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{"url":"https://example.com","source_lang":"en","target_lang":"es"}'
    ```
    """
    try:
        # Create job in DynamoDB and send to SQS
        job = create_job(
            user_id=user_id,
            url=str(request.url),
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )

        # Return immediate response
        return JobSubmitResponse(
            job_id=job.job_id,
            status=job.status,
            message="Translation job created. Use job_id to check progress.",
            poll_url=f"/api/jobs/{job.job_id}",
            created_at=job.created_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get translation job status and progress

    **Polling Recommendation:**
    - Poll every 2-3 seconds while status is "pending" or "processing"
    - Stop polling when status is "completed", "failed", or "cancelled"

    **Status Values:**
    - `pending`: Job queued, waiting for worker
    - `processing`: Worker is translating (check progress field)
    - `completed`: Translation finished (download_url available)
    - `failed`: Translation failed (see error_message)

    **Example:**
    ```bash
    curl -X GET /api/jobs/550e8400-e29b-41d4-a716-446655440000 \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify user owns this job
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")

    # Build response
    response = JobStatusResponse(
        job_id=job.job_id,
        user_id=job.user_id,
        status=job.status,
        url=job.url,
        source_lang=job.source_lang,
        target_lang=job.target_lang,
        progress=job.progress,
        pages_total=job.pages_total,
        pages_translated=job.pages_translated,
        words_total=job.words_total,
        words_translated=job.words_translated,
        created_at=job.created_at,
        updated_at=job.updated_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        failed_at=job.failed_at,
        message=job.message,
        error_message=job.error_message,
        result_url=job.result_url,
        download_url=job.download_url
    )

    return response


@router.get("", response_model=JobListResponse)
async def list_user_jobs(
    user_id: str = Depends(get_current_user_id),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Jobs per page")
):
    """
    List all translation jobs for current user

    **Sorting:** Newest jobs first (by created_at DESC)

    **Pagination:**
    - page: Page number (starts at 1)
    - page_size: Jobs per page (max 100)

    **Example:**
    ```bash
    curl -X GET /api/jobs?page=1&page_size=10 \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        # Get jobs from DynamoDB
        jobs, next_key = get_user_jobs(user_id, limit=page_size)

        # Convert to response format
        job_responses = []
        for job in jobs:
            job_resp = JobStatusResponse(
                job_id=job.job_id,
                user_id=job.user_id,
                status=job.status,
                url=job.url,
                source_lang=job.source_lang,
                target_lang=job.target_lang,
                progress=job.progress,
                pages_total=job.pages_total,
                pages_translated=job.pages_translated,
                words_total=job.words_total,
                words_translated=job.words_translated,
                created_at=job.created_at,
                updated_at=job.updated_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                failed_at=job.failed_at,
                message=job.message,
                error_message=job.error_message,
                result_url=job.result_url,
                download_url=job.download_url
            )

            job_responses.append(job_resp)

        return JobListResponse(
            jobs=job_responses,
            total=len(job_responses),
            page=page,
            page_size=page_size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.delete("/{job_id}", status_code=204)
async def cancel_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Cancel a translation job

    **Note:** If job is already processing, it may complete before cancellation takes effect.

    **Returns:** HTTP 204 No Content (success)

    **Example:**
    ```bash
    curl -X DELETE /api/jobs/550e8400-e29b-41d4-a716-446655440000 \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify user owns this job
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this job")

    # Only allow cancelling pending/processing jobs
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status: {job.status}")

    # Delete from DynamoDB
    success = delete_job(job_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel job")

    # Return 204 No Content
    return None


@router.get("/{job_id}/download")
async def download_translation(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate fresh presigned URL for downloading translated website

    Returns a redirect to S3 presigned URL (valid for 1 hour).
    This ensures the download link is always fresh and valid.

    Example:
    ```bash
    curl -X GET /api/jobs/550e8400-e29b-41d4-a716-446655440000/download \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -L  # Follow redirect
    ```
    """
    import boto3
    from fastapi.responses import RedirectResponse

    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify user owns this job
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to download this job")

    # Verify job is completed
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Job not completed yet (status: {job.status})")

    # Verify result_url exists
    if not job.result_url:
        raise HTTPException(status_code=404, detail="Translation result not found")

    # Parse S3 URL (format: s3://bucket/key)
    if not job.result_url.startswith('s3://'):
        raise HTTPException(status_code=500, detail="Invalid result URL format")

    s3_url_parts = job.result_url[5:].split('/', 1)
    if len(s3_url_parts) != 2:
        raise HTTPException(status_code=500, detail="Invalid S3 URL")

    bucket_name, file_key = s3_url_parts

    # Generate fresh presigned URL (valid for 1 hour)
    s3 = boto3.client('s3', region_name='eu-west-1')

    try:
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_key
            },
            ExpiresIn=3600  # 1 hour
        )

        # Return JSON with presigned URL (expires in 1 hour)
        return {
            "download_url": presigned_url,
            "expires_in": 3600,
            "filename": f"translated-site-{job_id}.zip"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")

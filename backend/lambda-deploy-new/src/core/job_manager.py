"""
Job Manager - DynamoDB and SQS operations for async translation jobs

This module handles all interactions with:
- DynamoDB (translation-jobs table) for job state persistence
- SQS (translatecloud-translation-queue) for asynchronous processing

Features:
- Create and track translation jobs
- Update job progress in real-time
- Query job status
- Send jobs to processing queue
- List user's jobs

Author: TranslateCloud Team
Last Updated: 2025-10-20
"""

import boto3
import uuid
import json
import logging
from typing import Optional, List
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

from src.schemas.job import DynamoDBJob, JobStatus

logger = logging.getLogger(__name__)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
sqs = boto3.client('sqs', region_name='eu-west-1')

# Configuration
TABLE_NAME = 'translation-jobs'
QUEUE_URL = 'https://sqs.eu-west-1.amazonaws.com/721096479937/translatecloud-translation-queue'
TTL_DAYS = 7  # Jobs auto-delete after 7 days

# Get table reference
jobs_table = dynamodb.Table(TABLE_NAME)


def create_job(user_id: str, url: str, source_lang: str, target_lang: str) -> DynamoDBJob:
    """
    Create a new translation job in DynamoDB and send to SQS queue

    Args:
        user_id (str): User ID from JWT token
        url (str): Website URL to translate
        source_lang (str): Source language code
        target_lang (str): Target language code

    Returns:
        DynamoDBJob: Created job object with job_id

    Raises:
        ClientError: If DynamoDB or SQS operation fails

    Example:
        >>> job = create_job("user123", "https://example.com", "en", "es")
        >>> print(job.job_id)
        "550e8400-e29b-41d4-a716-446655440000"
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    now = datetime.utcnow()
    now_iso = now.isoformat() + 'Z'
    ttl = int((now + timedelta(days=TTL_DAYS)).timestamp())

    # Create job object
    job = DynamoDBJob(
        job_id=job_id,
        user_id=user_id,
        status=JobStatus.PENDING,
        url=url,
        source_lang=source_lang,
        target_lang=target_lang,
        progress=0,
        created_at=now_iso,
        updated_at=now_iso,
        message="Job queued for processing...",
        ttl=ttl
    )

    try:
        # Save to DynamoDB
        jobs_table.put_item(Item=job.model_dump())
        logger.info(f"Created job {job_id} for user {user_id}")

        # Send message to SQS queue
        message_body = {
            "job_id": job_id,
            "user_id": user_id,
            "url": url,
            "source_lang": source_lang,
            "target_lang": target_lang
        }

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message_body),
            MessageAttributes={
                'job_id': {'StringValue': job_id, 'DataType': 'String'},
                'user_id': {'StringValue': user_id, 'DataType': 'String'}
            }
        )
        logger.info(f"Sent job {job_id} to SQS queue")

        return job

    except ClientError as e:
        logger.error(f"Failed to create job: {e}")
        raise


def get_job(job_id: str) -> Optional[DynamoDBJob]:
    """
    Retrieve job by ID from DynamoDB

    Args:
        job_id (str): Job UUID

    Returns:
        DynamoDBJob or None: Job object if found, None otherwise

    Example:
        >>> job = get_job("550e8400-e29b-41d4-a716-446655440000")
        >>> print(job.status)
        "processing"
    """
    try:
        response = jobs_table.get_item(Key={'job_id': job_id})

        if 'Item' in response:
            return DynamoDBJob(**response['Item'])

        return None

    except ClientError as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        return None


def update_job_status(
    job_id: str,
    status: JobStatus,
    progress: Optional[int] = None,
    pages_total: Optional[int] = None,
    pages_translated: Optional[int] = None,
    words_total: Optional[int] = None,
    words_translated: Optional[int] = None,
    message: Optional[str] = None,
    error_message: Optional[str] = None,
    result_url: Optional[str] = None,
    download_url: Optional[str] = None
) -> bool:
    """
    Update job status and progress in DynamoDB

    Args:
        job_id (str): Job UUID
        status (JobStatus): New status
        progress (int, optional): Progress percentage (0-100)
        pages_total (int, optional): Total pages discovered
        pages_translated (int, optional): Pages translated so far
        words_total (int, optional): Total words to translate
        words_translated (int, optional): Words translated so far
        message (str, optional): User-facing status message
        error_message (str, optional): Error details if failed
        result_url (str, optional): S3 URL of translated site (when completed)
        download_url (str, optional): Presigned URL for downloading result (expires in 7 days)

    Returns:
        bool: True if update succeeded, False otherwise

    Example:
        >>> update_job_status(
        ...     "550e8400-...",
        ...     JobStatus.PROCESSING,
        ...     progress=65,
        ...     pages_translated=7,
        ...     message="Translating page 7 of 10..."
        ... )
        True
    """
    try:
        now_iso = datetime.utcnow().isoformat() + 'Z'

        # Build update expression dynamically
        update_expr = "SET #status = :status, updated_at = :updated_at"
        expr_attr_names = {'#status': 'status'}
        expr_attr_values = {
            ':status': status.value,
            ':updated_at': now_iso
        }

        # Add optional fields
        if progress is not None:
            update_expr += ", progress = :progress"
            expr_attr_values[':progress'] = progress

        if pages_total is not None:
            update_expr += ", pages_total = :pages_total"
            expr_attr_values[':pages_total'] = pages_total

        if pages_translated is not None:
            update_expr += ", pages_translated = :pages_translated"
            expr_attr_values[':pages_translated'] = pages_translated

        if words_total is not None:
            update_expr += ", words_total = :words_total"
            expr_attr_values[':words_total'] = words_total

        if words_translated is not None:
            update_expr += ", words_translated = :words_translated"
            expr_attr_values[':words_translated'] = words_translated

        if message is not None:
            update_expr += ", message = :message"
            expr_attr_values[':message'] = message

        if error_message is not None:
            update_expr += ", error_message = :error_message"
            expr_attr_values[':error_message'] = error_message

        if result_url is not None:
            update_expr += ", result_url = :result_url"
            expr_attr_values[':result_url'] = result_url

        if download_url is not None:
            update_expr += ", download_url = :download_url"
            expr_attr_values[':download_url'] = download_url

        # Set timestamp for status transitions
        if status == JobStatus.PROCESSING:
            update_expr += ", started_at = :started_at"
            expr_attr_values[':started_at'] = now_iso
        elif status == JobStatus.COMPLETED:
            update_expr += ", completed_at = :completed_at"
            expr_attr_values[':completed_at'] = now_iso
        elif status == JobStatus.FAILED:
            update_expr += ", failed_at = :failed_at"
            expr_attr_values[':failed_at'] = now_iso

        # Execute update
        jobs_table.update_item(
            Key={'job_id': job_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values
        )

        logger.info(f"Updated job {job_id} to status {status.value}")
        return True

    except ClientError as e:
        logger.error(f"Failed to update job {job_id}: {e}")
        return False


def get_user_jobs(user_id: str, limit: int = 20, last_evaluated_key: Optional[dict] = None) -> tuple[List[DynamoDBJob], Optional[dict]]:
    """
    Get all jobs for a user, sorted by creation date (newest first)

    Uses GSI: user_id-created_at-index

    Args:
        user_id (str): User ID to query
        limit (int): Maximum number of jobs to return (default: 20)
        last_evaluated_key (dict, optional): Pagination token from previous query

    Returns:
        tuple: (list of jobs, pagination token for next page)

    Example:
        >>> jobs, next_token = get_user_jobs("user123", limit=10)
        >>> print(f"Found {len(jobs)} jobs")
        Found 10 jobs
    """
    try:
        query_kwargs = {
            'IndexName': 'user_id-created_at-index',
            'KeyConditionExpression': 'user_id = :user_id',
            'ExpressionAttributeValues': {':user_id': user_id},
            'Limit': limit,
            'ScanIndexForward': False  # Sort descending (newest first)
        }

        if last_evaluated_key:
            query_kwargs['ExclusiveStartKey'] = last_evaluated_key

        response = jobs_table.query(**query_kwargs)

        jobs = [DynamoDBJob(**item) for item in response.get('Items', [])]
        next_key = response.get('LastEvaluatedKey')

        return jobs, next_key

    except ClientError as e:
        logger.error(f"Failed to get jobs for user {user_id}: {e}")
        return [], None


def delete_job(job_id: str) -> bool:
    """
    Delete a job from DynamoDB (user cancellation)

    Args:
        job_id (str): Job UUID

    Returns:
        bool: True if deleted, False otherwise

    Note:
        This does NOT stop the worker if job is already processing.
        Worker will fail gracefully when it tries to update deleted job.
    """
    try:
        jobs_table.delete_item(Key={'job_id': job_id})
        logger.info(f"Deleted job {job_id}")
        return True

    except ClientError as e:
        logger.error(f"Failed to delete job {job_id}: {e}")
        return False

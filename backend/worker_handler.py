"""
Translation Worker Lambda Handler

Processes translation jobs from SQS queue asynchronously.
Triggered by SQS messages from translatecloud-translation-queue.

Flow:
1. Receive job from SQS
2. Update DynamoDB status to "processing"
3. Crawl website
4. Extract translatable text
5. Translate using DeepL/MarianMT
6. Build translated website
7. Upload to S3
8. Update DynamoDB status to "completed"

Author: TranslateCloud Team
Last Updated: 2025-10-20
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any

# Import core translation services
from src.core.web_extractor import WebExtractor
from src.core.translation_service import TranslationService
from src.core.html_reconstructor import HTMLReconstructor
from src.core.job_manager import update_job_status, get_job
from src.schemas.job import JobStatus
from src.config.settings import settings

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Lambda handler for processing translation jobs from SQS

    Args:
        event: SQS event containing job messages
        context: Lambda context object

    Returns:
        dict: Processing results
    """
    logger.info(f"Processing {len(event['Records'])} job(s) from SQS")

    results = {
        'successful': 0,
        'failed': 0,
        'errors': []
    }

    # Process each SQS message (should be 1 due to batch size)
    for record in event['Records']:
        try:
            # Parse message body
            message = json.loads(record['body'])
            job_id = message['job_id']

            logger.info(f"Processing job: {job_id}")

            # Process the translation job
            process_translation_job(
                job_id=job_id,
                user_id=message['user_id'],
                url=message['url'],
                source_lang=message['source_lang'],
                target_lang=message['target_lang']
            )

            results['successful'] += 1
            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            results['failed'] += 1
            error_msg = f"Job failed: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(f"Error processing job: {error_msg}")
            logger.error(traceback.format_exc())

            # Try to update job status to failed
            try:
                if 'job_id' in message:
                    update_job_status(
                        job_id=message['job_id'],
                        status=JobStatus.FAILED,
                        error_message=str(e)
                    )
            except Exception as update_error:
                logger.error(f"Failed to update job status: {update_error}")

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }


def process_translation_job(job_id: str, user_id: str, url: str, source_lang: str, target_lang: str):
    """
    Process a single translation job

    Args:
        job_id: Unique job identifier
        user_id: User who submitted the job
        url: Website URL to translate
        source_lang: Source language code
        target_lang: Target language code

    Raises:
        Exception: If any step fails
    """
    try:
        # ================================================================
        # Step 1: Initialize services
        # ================================================================
        logger.info(f"[{job_id}] Initializing translation services")

        extractor = WebExtractor()
        translator = TranslationService(deepl_api_key=settings.DEEPL_API_KEY)
        reconstructor = HTMLReconstructor()

        # Update status to processing
        update_job_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=0,
            message="Starting translation process..."
        )

        # ================================================================
        # Step 2: Crawl website
        # ================================================================
        logger.info(f"[{job_id}] Crawling website: {url}")

        update_job_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=5,
            message="Crawling website..."
        )

        crawl_result = extractor.crawl_website(url, max_pages=100)
        pages = crawl_result['pages']
        total_pages = len(pages)

        logger.info(f"[{job_id}] Found {total_pages} pages")

        update_job_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=15,
            pages_total=total_pages,
            message=f"Found {total_pages} pages to translate"
        )

        # ================================================================
        # Step 3: Extract translatable elements
        # ================================================================
        logger.info(f"[{job_id}] Extracting translatable text")

        all_elements = []
        total_words = 0

        for i, page in enumerate(pages):
            update_job_status(
                job_id=job_id,
                status=JobStatus.PROCESSING,
                progress=15 + int((i / total_pages) * 20),
                message=f"Extracting text from page {i+1} of {total_pages}..."
            )

            elements = extractor.extract_translatable_elements(page['html'], page['url'])
            all_elements.extend(elements)

            # Count words
            page_words = sum(len(el['text'].split()) for el in elements)
            total_words += page_words

        logger.info(f"[{job_id}] Extracted {len(all_elements)} elements ({total_words} words)")

        update_job_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=35,
            words_total=total_words,
            message=f"Translating {total_words} words..."
        )

        # ================================================================
        # Step 4: Translate elements
        # ================================================================
        logger.info(f"[{job_id}] Starting translation")

        translated_elements = []
        words_translated = 0

        for i, element in enumerate(all_elements):
            # Translate text
            translation_result = translator.translate(
                text=element['text'],
                source_lang=source_lang,
                target_lang=target_lang
            )

            if translation_result['success']:
                translated_element = element.copy()
                translated_element['text'] = translation_result['text']
                translated_elements.append(translated_element)

                # Update progress
                words_in_element = len(element['text'].split())
                words_translated += words_in_element

                progress = 35 + int((i / len(all_elements)) * 50)

                # Update every 10 elements to avoid too many DynamoDB writes
                if i % 10 == 0 or i == len(all_elements) - 1:
                    update_job_status(
                        job_id=job_id,
                        status=JobStatus.PROCESSING,
                        progress=progress,
                        words_translated=words_translated,
                        message=f"Translating... {int((i/len(all_elements))*100)}% complete"
                    )
            else:
                logger.warning(f"[{job_id}] Translation failed for element {i}: {translation_result.get('error')}")
                # Keep original text if translation fails
                translated_elements.append(element)

        logger.info(f"[{job_id}] Translation complete: {len(translated_elements)} elements")

        update_job_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=85,
            words_translated=words_translated,
            message="Building translated website..."
        )

        # ================================================================
        # Step 5: Reconstruct website
        # ================================================================
        logger.info(f"[{job_id}] Reconstructing translated website")

        zip_bytes = reconstructor.build_translated_site(
            pages=pages,
            translated_elements=translated_elements,
            source_lang=source_lang,
            target_lang=target_lang
        )

        update_job_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=95,
            message="Uploading translated website..."
        )

        # ================================================================
        # Step 6: Upload to S3
        # ================================================================
        logger.info(f"[{job_id}] Uploading to S3")

        import boto3
        s3 = boto3.client('s3', region_name='eu-west-1')

        bucket_name = 'translatecloud-translations-prod'
        file_key = f"jobs/{job_id}/translated-site.zip"

        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=zip_bytes,
            ContentType='application/zip',
            Metadata={
                'job_id': job_id,
                'user_id': user_id,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'pages': str(total_pages),
                'words': str(total_words)
            }
        )

        s3_url = f"s3://{bucket_name}/{file_key}"
        logger.info(f"[{job_id}] Uploaded to {s3_url}")

        # ================================================================
        # Step 7: Mark as completed
        # ================================================================
        update_job_status(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            pages_translated=total_pages,
            words_translated=words_translated,
            result_url=s3_url,
            message="Translation completed successfully!"
        )

        logger.info(f"[{job_id}] Job completed successfully")

    except Exception as e:
        logger.error(f"[{job_id}] Job failed: {str(e)}")
        logger.error(traceback.format_exc())

        # Update job status to failed
        update_job_status(
            job_id=job_id,
            status=JobStatus.FAILED,
            error_message=f"Translation failed: {str(e)}"
        )

        raise

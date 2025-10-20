# Async Translation Architecture

**Status:** Implementation in Progress
**Created:** 2025-10-20
**Version:** 1.0

## Problem Statement

The current synchronous architecture has a critical limitation:

- **API Gateway Timeout:** 30 seconds maximum
- **Lambda Timeout:** 300 seconds (5 minutes)
- **Bottleneck:** API Gateway kills requests after 30s even if Lambda is still processing

**Impact:**
- Small websites (1-5 pages): ✅ Works fine (~5-15 seconds)
- Medium websites (10-20 pages): ⚠️ May timeout
- Large websites (50+ pages): ❌ Always fails

## Solution: Async Job Queue Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER WORKFLOW                            │
└─────────────────────────────────────────────────────────────────┘

1. SUBMIT JOB
   Browser → POST /api/jobs/translate
           → API Gateway (instant response)
           → Lambda API Handler
           → Creates job in DynamoDB (status: pending)
           → Sends message to SQS Queue
           ← Returns job_id (< 1 second)

2. PROCESS JOB (Background)
   SQS Queue → Triggers Lambda Worker
             → Updates DynamoDB (status: processing)
             → Crawls website
             → Translates content (can take 5-15 minutes)
             → Updates DynamoDB (status: completed)

3. POLL STATUS
   Browser → GET /api/jobs/{job_id}/status (every 2 seconds)
           → API Gateway
           → Lambda API Handler
           → Reads from DynamoDB
           ← Returns {status, progress, result}
```

### AWS Components

#### 1. **DynamoDB Table: `translation-jobs`**
```
Primary Key: job_id (String, UUID)

Attributes:
- job_id: "550e8400-e29b-41d4-a716-446655440000"
- user_id: "user123"
- status: "pending" | "processing" | "completed" | "failed"
- url: "https://example.com"
- source_lang: "en"
- target_lang: "es"
- progress: 65  (percentage 0-100)
- pages_total: 10
- pages_translated: 7
- words_total: 5000
- words_translated: 3500
- created_at: "2025-10-20T15:30:00Z"
- updated_at: "2025-10-20T15:32:45Z"
- started_at: "2025-10-20T15:30:05Z"
- completed_at: "2025-10-20T15:35:20Z"
- result_url: "s3://translatecloud-translations-prod/550e8400.zip"
- error_message: null
- ttl: 1735689000  (auto-delete after 7 days)
```

**Indexes:**
- GSI: `user_id-created_at-index` (for listing user's jobs)

**Auto-delete:** TTL enabled (jobs deleted after 7 days)

#### 2. **SQS Queue: `translatecloud-translation-queue`**
```
Type: Standard Queue
Visibility Timeout: 900 seconds (15 minutes)
Message Retention: 4 days
Dead Letter Queue: translatecloud-translation-dlq (after 3 retries)
Max Receive Count: 3

Message Format:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "url": "https://example.com",
  "source_lang": "en",
  "target_lang": "es"
}
```

#### 3. **Lambda Functions**

**A. API Handler (existing: translatecloud-api)**
- **Role:** Receives HTTP requests, manages job lifecycle
- **Timeout:** 30 seconds (matches API Gateway)
- **Memory:** 512 MB
- **Endpoints:**
  - `POST /api/jobs/translate` - Submit new job
  - `GET /api/jobs/{job_id}` - Get job status
  - `GET /api/jobs` - List user's jobs
  - `DELETE /api/jobs/{job_id}` - Cancel job

**B. Worker Function (new: translatecloud-translation-worker)**
- **Role:** Processes translation jobs from SQS
- **Timeout:** 900 seconds (15 minutes)
- **Memory:** 2048 MB (needs more RAM for crawling/translating)
- **Trigger:** SQS Queue
- **Batch Size:** 1 (process one job at a time)
- **Reserved Concurrency:** 5 (max 5 translations in parallel)

### API Endpoints

#### POST /api/jobs/translate
**Request:**
```json
{
  "url": "https://example.com",
  "source_lang": "en",
  "target_lang": "es"
}
```

**Response (immediate, < 1 second):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Translation job created. Use job_id to check progress.",
  "poll_url": "/api/jobs/550e8400-e29b-41d4-a716-446655440000"
}
```

#### GET /api/jobs/{job_id}
**Response (pending):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0,
  "created_at": "2025-10-20T15:30:00Z",
  "message": "Job is in queue..."
}
```

**Response (processing):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "pages_total": 10,
  "pages_translated": 7,
  "words_total": 5000,
  "words_translated": 3500,
  "created_at": "2025-10-20T15:30:00Z",
  "started_at": "2025-10-20T15:30:05Z",
  "message": "Translating page 7 of 10..."
}
```

**Response (completed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "pages_total": 10,
  "pages_translated": 10,
  "words_total": 5000,
  "words_translated": 5000,
  "created_at": "2025-10-20T15:30:00Z",
  "completed_at": "2025-10-20T15:35:20Z",
  "download_url": "https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/jobs/550e8400.../download",
  "message": "Translation completed successfully!"
}
```

**Response (failed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 45,
  "error_message": "DeepL API rate limit exceeded. Please try again later.",
  "created_at": "2025-10-20T15:30:00Z",
  "failed_at": "2025-10-20T15:32:15Z"
}
```

### Frontend Flow

```javascript
// 1. Submit translation job
const response = await fetch('/api/jobs/translate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://example.com',
    source_lang: 'en',
    target_lang: 'es'
  })
});

const { job_id } = await response.json();

// 2. Poll for status every 2 seconds
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch(`/api/jobs/${job_id}`);
  const job = await statusResponse.json();

  // Update UI with progress
  updateProgressBar(job.progress);
  updateStatusMessage(job.message);

  if (job.status === 'completed') {
    clearInterval(pollInterval);
    showDownloadButton(job.download_url);
  } else if (job.status === 'failed') {
    clearInterval(pollInterval);
    showError(job.error_message);
  }
}, 2000);
```

### Worker Processing Logic

```python
def process_job(job_id, url, source_lang, target_lang, user_id):
    """
    Worker function that processes translation job from SQS
    """
    try:
        # 1. Update status to processing
        update_job_status(job_id, 'processing', progress=0)

        # 2. Crawl website
        pages = crawl_website(url)
        update_job_status(job_id, 'processing',
                         pages_total=len(pages),
                         progress=10)

        # 3. Extract text from pages
        elements = []
        for i, page in enumerate(pages):
            page_elements = extract_text(page)
            elements.extend(page_elements)
            progress = 10 + (i / len(pages)) * 30
            update_job_status(job_id, 'processing', progress=progress)

        # 4. Translate elements
        translated = []
        for i, element in enumerate(elements):
            translated_text = translate(element.text, source_lang, target_lang)
            translated.append({...element, text: translated_text})
            progress = 40 + (i / len(elements)) * 50
            update_job_status(job_id, 'processing',
                             progress=progress,
                             words_translated=i * avg_words_per_element)

        # 5. Build translated website
        zip_file = build_website(pages, translated)
        update_job_status(job_id, 'processing', progress=95)

        # 6. Upload to S3
        s3_url = upload_to_s3(zip_file, job_id)

        # 7. Mark as completed
        update_job_status(job_id, 'completed',
                         progress=100,
                         result_url=s3_url,
                         pages_translated=len(pages))

    except Exception as e:
        # Handle failure
        update_job_status(job_id, 'failed',
                         error_message=str(e))
        raise
```

## Benefits

### ✅ Scalability
- No 30-second timeout limitation
- Can process websites with 100+ pages
- Multiple jobs can run in parallel (up to 5 concurrent)

### ✅ User Experience
- Instant feedback (job_id returned immediately)
- Real-time progress updates (every 2 seconds)
- Clear status messages ("Translating page 7 of 10...")

### ✅ Reliability
- Jobs survive Lambda restarts
- Dead Letter Queue catches failed jobs
- Automatic retries (up to 3 times)
- Auto-cleanup after 7 days (DynamoDB TTL)

### ✅ Cost Efficiency
- Workers only run when needed
- SQS is cheap ($0.40 per 1M requests)
- DynamoDB on-demand pricing (pay per read/write)

## Implementation Plan

### Phase 1: Infrastructure (30 minutes)
1. Create DynamoDB table
2. Create SQS queue + Dead Letter Queue
3. Update IAM roles

### Phase 2: Backend Code (1 hour)
1. Create job submission endpoint
2. Create job status endpoint
3. Create worker Lambda function
4. Add progress tracking to translation logic

### Phase 3: Deployment (30 minutes)
1. Deploy worker Lambda
2. Configure SQS trigger
3. Test end-to-end flow

### Phase 4: Frontend (1 hour)
1. Update translate.html with polling
2. Add progress bar UI
3. Add status messages
4. Handle errors gracefully

**Total Time:** ~3 hours

## Cost Estimate

### Additional Monthly Costs

| Service | Usage | Cost |
|---------|-------|------|
| DynamoDB | 10k jobs/month, 7-day retention | €2 |
| SQS | 10k messages/month | €0.004 |
| Lambda Worker | 10k invocations, 2GB RAM, 2 min avg | €5 |
| S3 Storage | Translation results (auto-delete) | €1 |
| **TOTAL INCREASE** | | **~€8/month** |

**New Monthly Total:** €34 + €8 = **€42/month**

## Monitoring & Alerts

### CloudWatch Metrics
- `JobsSubmitted` - Count of new jobs
- `JobsCompleted` - Successful completions
- `JobsFailed` - Failures
- `AverageProcessingTime` - Time from submit to complete
- `QueueDepth` - SQS queue length

### Alarms
- Alert if queue depth > 50 (backlog building)
- Alert if failure rate > 10%
- Alert if average processing time > 10 minutes

## Future Enhancements

### Phase 2 (Future)
- **Priority Queue:** VIP users get faster processing
- **Batch Jobs:** Upload CSV with 100 URLs
- **Webhooks:** Notify user when job completes
- **Email Notifications:** Send email with download link
- **Job Cancellation:** Stop in-progress jobs
- **Result Caching:** Reuse translations for same URL

---

**Next Steps:**
1. Create DynamoDB table
2. Create SQS queue
3. Implement job endpoints
4. Create worker Lambda
5. Test with large website

**Author:** TranslateCloud Team
**Last Updated:** 2025-10-20

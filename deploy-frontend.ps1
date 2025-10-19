#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy TranslateCloud Frontend to S3 + Invalidate CloudFront Cache

.DESCRIPTION
    Complete deployment script that:
    1. Syncs frontend files to S3
    2. Sets proper cache headers
    3. ALWAYS invalidates CloudFront distribution
    4. Waits for invalidation to complete
    5. Verifies deployment

.PARAMETER SkipInvalidation
    Skip CloudFront invalidation (NOT RECOMMENDED)

.EXAMPLE
    .\deploy-frontend.ps1
    # Full deployment with CloudFront invalidation

.EXAMPLE
    .\deploy-frontend.ps1 -SkipInvalidation
    # Deploy without invalidating cache (for testing only)

#>

param(
    [switch]$SkipInvalidation = $false
)

# Configuration
$S3_BUCKET = "translatecloud-frontend-prod"
$CLOUDFRONT_ID = "E1PKVM5C703IXO"
$AWS_REGION = "eu-west-1"
$FRONTEND_DIR = "frontend/public"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TranslateCloud Frontend Deployment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Verify AWS credentials
Write-Host "[1/6] Verifying AWS credentials..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity --query "Account" --output text 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "AWS credentials not configured"
    }
    Write-Host "      AWS Account: $identity" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Check if frontend directory exists
Write-Host "`n[2/6] Checking frontend directory..." -ForegroundColor Yellow
if (-not (Test-Path $FRONTEND_DIR)) {
    Write-Host "      ERROR: Frontend directory not found: $FRONTEND_DIR" -ForegroundColor Red
    exit 1
}
Write-Host "      Frontend directory found" -ForegroundColor Green

# Step 3: Sync files to S3 with proper cache headers
Write-Host "`n[3/6] Syncing files to S3..." -ForegroundColor Yellow

# Upload HTML files with short cache (5 minutes)
Write-Host "      Uploading HTML files (5min cache)..." -ForegroundColor Gray
aws s3 sync $FRONTEND_DIR s3://$S3_BUCKET/ `
    --region $AWS_REGION `
    --exclude "*" `
    --include "*.html" `
    --cache-control "public, max-age=300, must-revalidate" `
    --metadata-directive REPLACE

# Upload JS/CSS with medium cache (1 hour)
Write-Host "      Uploading JS/CSS files (1hr cache)..." -ForegroundColor Gray
aws s3 sync $FRONTEND_DIR s3://$S3_BUCKET/ `
    --region $AWS_REGION `
    --exclude "*" `
    --include "*.js" --include "*.css" `
    --cache-control "public, max-age=3600" `
    --metadata-directive REPLACE

# Upload images with long cache (1 day)
Write-Host "      Uploading images (1day cache)..." -ForegroundColor Gray
aws s3 sync $FRONTEND_DIR s3://$S3_BUCKET/ `
    --region $AWS_REGION `
    --exclude "*" `
    --include "*.jpg" --include "*.jpeg" --include "*.png" --include "*.gif" --include "*.svg" --include "*.webp" `
    --cache-control "public, max-age=86400" `
    --metadata-directive REPLACE

# Upload everything else
Write-Host "      Uploading remaining files..." -ForegroundColor Gray
aws s3 sync $FRONTEND_DIR s3://$S3_BUCKET/ `
    --region $AWS_REGION `
    --delete

if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERROR: S3 sync failed" -ForegroundColor Red
    exit 1
}
Write-Host "      Files synced successfully" -ForegroundColor Green

# Step 4: Create CloudFront invalidation
if (-not $SkipInvalidation) {
    Write-Host "`n[4/6] Creating CloudFront invalidation..." -ForegroundColor Yellow

    $invalidation = aws cloudfront create-invalidation `
        --distribution-id $CLOUDFRONT_ID `
        --paths "/*" `
        --region us-east-1 `
        --output json | ConvertFrom-Json

    if ($LASTEXITCODE -ne 0) {
        Write-Host "      ERROR: CloudFront invalidation failed" -ForegroundColor Red
        exit 1
    }

    $invalidationId = $invalidation.Invalidation.Id
    Write-Host "      Invalidation ID: $invalidationId" -ForegroundColor Green

    # Step 5: Wait for invalidation to complete
    Write-Host "`n[5/6] Waiting for CloudFront invalidation..." -ForegroundColor Yellow
    Write-Host "      This may take 1-3 minutes..." -ForegroundColor Gray

    $maxAttempts = 60
    $attempt = 0

    while ($attempt -lt $maxAttempts) {
        $status = aws cloudfront get-invalidation `
            --distribution-id $CLOUDFRONT_ID `
            --id $invalidationId `
            --region us-east-1 `
            --query "Invalidation.Status" `
            --output text

        if ($status -eq "Completed") {
            Write-Host "      Invalidation completed!" -ForegroundColor Green
            break
        }

        $attempt++
        Write-Host "      Status: $status (attempt $attempt/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }

    if ($attempt -ge $maxAttempts) {
        Write-Host "      WARNING: Invalidation taking longer than expected" -ForegroundColor Yellow
        Write-Host "      Check status manually: aws cloudfront get-invalidation --distribution-id $CLOUDFRONT_ID --id $invalidationId" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[4/6] SKIPPED: CloudFront invalidation" -ForegroundColor Yellow
    Write-Host "      WARNING: Users may see cached old content!" -ForegroundColor Red
    Write-Host "`n[5/6] SKIPPED: Waiting for invalidation" -ForegroundColor Yellow
}

# Step 6: Verify deployment
Write-Host "`n[6/6] Verifying deployment..." -ForegroundColor Yellow

# Check critical files
$criticalFiles = @(
    "index.html",
    "en/login.html",
    "en/signup.html",
    "assets/js/auth.js",
    "assets/js/api.js"
)

$allPresent = $true
foreach ($file in $criticalFiles) {
    $exists = aws s3 ls "s3://$S3_BUCKET/$file" --region $AWS_REGION 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      OK: $file" -ForegroundColor Green
    } else {
        Write-Host "      MISSING: $file" -ForegroundColor Red
        $allPresent = $false
    }
}

# Final summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "S3 Bucket:       $S3_BUCKET" -ForegroundColor White
Write-Host "CloudFront ID:   $CLOUDFRONT_ID" -ForegroundColor White
Write-Host "Region:          $AWS_REGION" -ForegroundColor White

if ($allPresent) {
    Write-Host "Status:          SUCCESS" -ForegroundColor Green
    Write-Host "`nYour site should be updated in 1-3 minutes at:" -ForegroundColor Green
    Write-Host "https://www.translatecloud.io" -ForegroundColor Cyan
} else {
    Write-Host "Status:          WARNING - Some files missing" -ForegroundColor Yellow
}

if (-not $SkipInvalidation) {
    Write-Host "`nCloudFront cache has been invalidated." -ForegroundColor Green
    Write-Host "Users will see new content immediately after invalidation completes." -ForegroundColor Green
} else {
    Write-Host "`nWARNING: CloudFront cache NOT invalidated!" -ForegroundColor Red
    Write-Host "Users may continue seeing old cached content." -ForegroundColor Red
}

Write-Host "========================================`n" -ForegroundColor Cyan

exit 0

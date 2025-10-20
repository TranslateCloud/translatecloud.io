# ============================================================================
# Deploy Translation Worker Lambda
# ============================================================================
# Creates deployment package for the worker Lambda function and deploys to AWS
# Worker processes translation jobs from SQS queue asynchronously

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TRANSLATECLOUD - DEPLOY WORKER LAMBDA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Configuration
$BackendDir = "backend"
$DeployDir = "$BackendDir/worker-deploy"
$ZipFile = "$BackendDir/translatecloud-worker.zip"
$FunctionName = "translatecloud-translation-worker"
$Region = "eu-west-1"
$RoleArn = "arn:aws:iam::721096479937:role/translatecloud-worker-lambda-role"

# ============================================================================
# Step 1: Clean previous deployment
# ============================================================================
Write-Host "[1/6] Cleaning previous deployment..." -ForegroundColor Yellow

if (Test-Path $DeployDir) {
    Remove-Item -Path $DeployDir -Recurse -Force
    Write-Host "  ✅ Removed old deployment directory" -ForegroundColor Green
}

if (Test-Path $ZipFile) {
    Remove-Item -Path $ZipFile -Force
    Write-Host "  ✅ Removed old ZIP file" -ForegroundColor Green
}

New-Item -ItemType Directory -Path $DeployDir | Out-Null
Write-Host "  ✅ Created fresh deployment directory" -ForegroundColor Green

# ============================================================================
# Step 2: Copy source code
# ============================================================================
Write-Host "`n[2/6] Copying source code..." -ForegroundColor Yellow

# Copy worker handler
Copy-Item -Path "$BackendDir/worker_handler.py" -Destination $DeployDir
Write-Host "  ✅ Copied worker_handler.py" -ForegroundColor Green

# Copy entire src directory
Copy-Item -Path "$BackendDir/src" -Destination "$DeployDir/src" -Recurse
Write-Host "  ✅ Copied src/ directory" -ForegroundColor Green

# Copy requirements.txt
Copy-Item -Path "$BackendDir/requirements.txt" -Destination $DeployDir
Write-Host "  ✅ Copied requirements.txt" -ForegroundColor Green

# ============================================================================
# Step 3: Install Python dependencies
# ============================================================================
Write-Host "`n[3/6] Installing Python dependencies..." -ForegroundColor Yellow

# Install to deployment directory
pip install -r "$BackendDir/requirements.txt" -t $DeployDir --quiet

if ($?) {
    Write-Host "  ✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Step 4: Create deployment ZIP (Linux-compatible)
# ============================================================================
Write-Host "`n[4/6] Creating deployment package..." -ForegroundColor Yellow

# Use Python to create Linux-compatible ZIP
python -c @"
import zipfile
import os
from pathlib import Path

deploy_dir = Path('$DeployDir')
zip_file = Path('$ZipFile')

with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(deploy_dir):
        for file in files:
            file_path = Path(root) / file
            arcname = file_path.relative_to(deploy_dir).as_posix()
            zipf.write(file_path, arcname)

print(f'Created {zip_file.name}: {os.path.getsize(zip_file) / 1024 / 1024:.2f} MB')
"@

if (Test-Path $ZipFile) {
    $ZipSize = (Get-Item $ZipFile).Length / 1MB
    Write-Host "  ✅ Created deployment package: $([math]::Round($ZipSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to create ZIP file" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Step 5: Deploy to AWS Lambda
# ============================================================================
Write-Host "`n[5/6] Deploying to AWS Lambda..." -ForegroundColor Yellow

# Check if function exists
$FunctionExists = aws lambda get-function --function-name $FunctionName --region $Region 2>&1

if ($LASTEXITCODE -eq 0) {
    # Update existing function
    Write-Host "  → Updating existing function..." -ForegroundColor Cyan

    aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file "fileb://$ZipFile" `
        --region $Region | Out-Null

    if ($?) {
        Write-Host "  ✅ Function code updated" -ForegroundColor Green

        # Update configuration
        aws lambda update-function-configuration `
            --function-name $FunctionName `
            --timeout 900 `
            --memory-size 2048 `
            --environment "Variables={DEEPL_API_KEY=$env:DEEPL_API_KEY}" `
            --region $Region | Out-Null

        if ($?) {
            Write-Host "  ✅ Function configuration updated" -ForegroundColor Green
        }
    } else {
        Write-Host "  ❌ Failed to update function" -ForegroundColor Red
        exit 1
    }
} else {
    # Create new function
    Write-Host "  → Creating new function..." -ForegroundColor Cyan

    aws lambda create-function `
        --function-name $FunctionName `
        --runtime python3.11 `
        --role $RoleArn `
        --handler worker_handler.handler `
        --zip-file "fileb://$ZipFile" `
        --timeout 900 `
        --memory-size 2048 `
        --environment "Variables={DEEPL_API_KEY=$env:DEEPL_API_KEY}" `
        --description "TranslateCloud translation worker - processes jobs from SQS queue" `
        --region $Region | Out-Null

    if ($?) {
        Write-Host "  ✅ Function created successfully" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Failed to create function" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# Step 6: Configure SQS trigger
# ============================================================================
Write-Host "`n[6/6] Configuring SQS trigger..." -ForegroundColor Yellow

$QueueUrl = "https://sqs.eu-west-1.amazonaws.com/721096479937/translatecloud-translation-queue"
$QueueArn = "arn:aws:sqs:eu-west-1:721096479937:translatecloud-translation-queue"

# Check if event source mapping exists
$EventSourceMappings = aws lambda list-event-source-mappings `
    --function-name $FunctionName `
    --region $Region | ConvertFrom-Json

$ExistingMapping = $EventSourceMappings.EventSourceMappings | Where-Object { $_.EventSourceArn -eq $QueueArn }

if ($ExistingMapping) {
    Write-Host "  → SQS trigger already configured" -ForegroundColor Cyan
    Write-Host "  ✅ Event source mapping UUID: $($ExistingMapping.UUID)" -ForegroundColor Green
} else {
    # Create event source mapping
    aws lambda create-event-source-mapping `
        --function-name $FunctionName `
        --event-source-arn $QueueArn `
        --batch-size 1 `
        --region $Region | Out-Null

    if ($?) {
        Write-Host "  ✅ SQS trigger configured (batch size: 1)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Failed to configure SQS trigger - may need manual setup" -ForegroundColor Yellow
    }
}

# ============================================================================
# Deployment Summary
# ============================================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Function Name:   $FunctionName" -ForegroundColor White
Write-Host "Runtime:         Python 3.11" -ForegroundColor White
Write-Host "Timeout:         900 seconds (15 minutes)" -ForegroundColor White
Write-Host "Memory:          2048 MB" -ForegroundColor White
Write-Host "Trigger:         SQS Queue (translatecloud-translation-queue)" -ForegroundColor White
Write-Host "Region:          $Region" -ForegroundColor White

Write-Host "`n✅ Worker Lambda is ready to process translation jobs!`n" -ForegroundColor Green

# ============================================================================
# Cleanup
# ============================================================================
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Path $DeployDir -Recurse -Force
Write-Host "✅ Cleanup complete`n" -ForegroundColor Green

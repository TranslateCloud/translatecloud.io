# TranslateCloud Lambda Deployment Script
# Creates a properly structured ZIP and uploads to AWS Lambda

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TranslateCloud Lambda Deployment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$LAMBDA_NAME = "translatecloud-api"
$DEPLOY_DIR = "lambda-deploy-new"
$ZIP_NAME = "translatecloud-api-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"

# Step 1: Clean previous deployment folder
Write-Host "[1/6] Cleaning previous deployment..." -ForegroundColor Yellow
if (Test-Path $DEPLOY_DIR) {
    Remove-Item -Path $DEPLOY_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $DEPLOY_DIR | Out-Null
Write-Host "✅ Clean deployment folder created`n" -ForegroundColor Green

# Step 2: Copy lambda_handler.py to root
Write-Host "[2/6] Copying lambda_handler.py..." -ForegroundColor Yellow
if (Test-Path "lambda_handler.py") {
    Copy-Item -Path "lambda_handler.py" -Destination $DEPLOY_DIR
    Write-Host "✅ lambda_handler.py copied`n" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: lambda_handler.py not found!" -ForegroundColor Red
    exit 1
}

# Step 3: Copy src/ directory
Write-Host "[3/6] Copying src/ directory..." -ForegroundColor Yellow
if (Test-Path "src") {
    Copy-Item -Path "src" -Destination $DEPLOY_DIR -Recurse
    # Remove __pycache__ folders
    Get-ChildItem -Path "$DEPLOY_DIR\src" -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Write-Host "✅ src/ directory copied (cleaned __pycache__)`n" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: src/ directory not found!" -ForegroundColor Red
    exit 1
}

# Step 4: Install dependencies
Write-Host "[4/6] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take 2-3 minutes...`n" -ForegroundColor Gray

# Install dependencies for Linux (Lambda platform)
pip install --target="$DEPLOY_DIR" `
    --platform manylinux2014_x86_64 `
    --implementation cp `
    --python-version 3.11 `
    --only-binary=:all: `
    fastapi `
    mangum `
    psycopg2-binary `
    python-jose[cryptography] `
    passlib[bcrypt] `
    python-multipart `
    requests `
    beautifulsoup4 `
    lxml `
    deepl `
    python-dotenv `
    pydantic-settings `
    email-validator `
    --upgrade `
    --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed (Linux binaries)`n" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: Some dependencies may have failed`n" -ForegroundColor Yellow
}

# Step 5: Create ZIP file
Write-Host "[5/6] Creating deployment ZIP..." -ForegroundColor Yellow
$currentLocation = Get-Location
Set-Location $DEPLOY_DIR

# Create ZIP with all contents
Compress-Archive -Path * -DestinationPath "..\$ZIP_NAME" -Force

Set-Location $currentLocation
Write-Host "✅ ZIP created: $ZIP_NAME`n" -ForegroundColor Green

# Display ZIP contents
Write-Host "ZIP Structure:" -ForegroundColor Cyan
Expand-Archive -Path $ZIP_NAME -DestinationPath "temp-verify" -Force
Get-ChildItem "temp-verify" -Recurse -Depth 1 | Select-Object -First 20 | Format-Table Name, Length
Remove-Item "temp-verify" -Recurse -Force
Write-Host ""

# Step 6: Upload to Lambda
Write-Host "[6/6] Uploading to AWS Lambda..." -ForegroundColor Yellow
Write-Host "Function: $LAMBDA_NAME" -ForegroundColor Gray
Write-Host "Region: eu-west-1`n" -ForegroundColor Gray

$zipPath = (Get-Item $ZIP_NAME).FullName
aws lambda update-function-code `
    --function-name $LAMBDA_NAME `
    --zip-file "fileb://$zipPath" `
    --region eu-west-1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Lambda function updated successfully!`n" -ForegroundColor Green

    # Wait for update to complete
    Write-Host "Waiting for Lambda to finish updating..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5

    # Check status
    $status = aws lambda get-function-configuration --function-name $LAMBDA_NAME --query "LastUpdateStatus" --output text
    Write-Host "Update Status: $status`n" -ForegroundColor Cyan

} else {
    Write-Host "`n❌ ERROR: Failed to upload to Lambda" -ForegroundColor Red
    Write-Host "Check that you have AWS credentials configured`n" -ForegroundColor Yellow
    exit 1
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Lambda Function: $LAMBDA_NAME" -ForegroundColor White
Write-Host "ZIP File: $ZIP_NAME" -ForegroundColor White
Write-Host "Size: $((Get-Item $ZIP_NAME).Length / 1MB) MB`n" -ForegroundColor White

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test your API endpoint" -ForegroundColor White
Write-Host "2. Check CloudWatch logs if there are errors" -ForegroundColor White
Write-Host "3. Configure CORS in API Gateway if needed`n" -ForegroundColor White

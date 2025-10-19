#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy TranslateCloud Backend to AWS Lambda

.DESCRIPTION
    Complete backend deployment script that:
    1. Installs dependencies to lambda-deploy folder
    2. Copies source code
    3. Creates deployment ZIP
    4. Uploads to Lambda
    5. Waits for deployment to complete
    6. Verifies function is active

.EXAMPLE
    .\deploy-backend.ps1
    # Full backend deployment to Lambda

#>

# Configuration
$FUNCTION_NAME = "translatecloud-api"
$AWS_REGION = "eu-west-1"
$PYTHON_VERSION = "3.11"
$BACKEND_DIR = "backend"
$DEPLOY_DIR = "$BACKEND_DIR/lambda-deploy"
$ZIP_FILE = "$BACKEND_DIR/translatecloud-api-PRODUCTION.zip"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TranslateCloud Backend Deployment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Verify prerequisites
Write-Host "[1/8] Verifying prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "      Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: Python not found" -ForegroundColor Red
    exit 1
}

# Check AWS CLI
try {
    $awsVersion = aws --version 2>&1
    Write-Host "      AWS CLI: $($awsVersion.Split()[0])" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: AWS CLI not found" -ForegroundColor Red
    exit 1
}

# Check backend directory
if (-not (Test-Path $BACKEND_DIR)) {
    Write-Host "      ERROR: Backend directory not found" -ForegroundColor Red
    exit 1
}
Write-Host "      Backend directory found" -ForegroundColor Green

# Step 2: Clean and prepare deployment directory
Write-Host "`n[2/8] Preparing deployment directory..." -ForegroundColor Yellow

if (Test-Path $DEPLOY_DIR) {
    Write-Host "      Cleaning existing deployment directory..." -ForegroundColor Gray
    Remove-Item -Recurse -Force $DEPLOY_DIR
}

New-Item -ItemType Directory -Path $DEPLOY_DIR -Force | Out-Null
Write-Host "      Deployment directory ready" -ForegroundColor Green

# Step 3: Install Python dependencies
Write-Host "`n[3/8] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "      This may take 2-3 minutes..." -ForegroundColor Gray

$pipCommand = "pip install -r $BACKEND_DIR/requirements.txt -t $DEPLOY_DIR --platform manylinux2014_x86_64 --python-version 3.11 --implementation cp --only-binary=:all: --upgrade"

try {
    Invoke-Expression $pipCommand 2>&1 | Out-Null

    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed"
    }

    Write-Host "      Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "      Try: pip install --upgrade pip" -ForegroundColor Yellow
    exit 1
}

# Step 4: Copy source code
Write-Host "`n[4/8] Copying source code..." -ForegroundColor Yellow

# Copy src directory
Copy-Item -Path "$BACKEND_DIR/src" -Destination "$DEPLOY_DIR/src" -Recurse -Force

# Copy lambda handler
Copy-Item -Path "$BACKEND_DIR/lambda_handler.py" -Destination "$DEPLOY_DIR/" -Force

# Verify critical files
$criticalFiles = @(
    "$DEPLOY_DIR/lambda_handler.py",
    "$DEPLOY_DIR/src/main.py",
    "$DEPLOY_DIR/src/api/routes/auth.py",
    "$DEPLOY_DIR/src/core/translation_service.py"
)

$allPresent = $true
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "      OK: $($file.Replace($DEPLOY_DIR + '\', ''))" -ForegroundColor Green
    } else {
        Write-Host "      MISSING: $($file.Replace($DEPLOY_DIR + '\', ''))" -ForegroundColor Red
        $allPresent = $false
    }
}

if (-not $allPresent) {
    Write-Host "      ERROR: Missing critical files" -ForegroundColor Red
    exit 1
}

# Step 5: Create deployment ZIP
Write-Host "`n[5/8] Creating deployment package..." -ForegroundColor Yellow

# Remove old ZIP if exists
if (Test-Path $ZIP_FILE) {
    Remove-Item $ZIP_FILE -Force
}

# Create ZIP
try {
    $deployDirAbsolute = Resolve-Path $DEPLOY_DIR
    Set-Location $deployDirAbsolute

    Compress-Archive -Path * -DestinationPath (Resolve-Path "..\translatecloud-api-PRODUCTION.zip") -Force

    Set-Location (Split-Path $deployDirAbsolute -Parent)
    Set-Location ..

    $zipInfo = Get-Item $ZIP_FILE
    $sizeMB = [math]::Round($zipInfo.Length / 1MB, 2)

    Write-Host "      Package created: $sizeMB MB" -ForegroundColor Green

    if ($sizeMB -gt 50) {
        Write-Host "      WARNING: Package is large ($sizeMB MB)" -ForegroundColor Yellow
        Write-Host "      Lambda limit is 50MB (zipped), 250MB (unzipped)" -ForegroundColor Yellow
    }

} catch {
    Write-Host "      ERROR: Failed to create ZIP: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Upload to Lambda
Write-Host "`n[6/8] Uploading to Lambda..." -ForegroundColor Yellow
Write-Host "      Function: $FUNCTION_NAME" -ForegroundColor Gray
Write-Host "      Region: $AWS_REGION" -ForegroundColor Gray

try {
    $uploadResult = aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://$ZIP_FILE `
        --region $AWS_REGION `
        --output json 2>&1 | ConvertFrom-Json

    if ($LASTEXITCODE -ne 0) {
        throw "Lambda update failed"
    }

    $lastModified = $uploadResult.LastModified
    $codeSize = [math]::Round($uploadResult.CodeSize / 1MB, 2)

    Write-Host "      Upload complete!" -ForegroundColor Green
    Write-Host "      Code size: $codeSize MB" -ForegroundColor Gray
    Write-Host "      Last modified: $lastModified" -ForegroundColor Gray

} catch {
    Write-Host "      ERROR: Failed to upload to Lambda" -ForegroundColor Red
    Write-Host "      $_" -ForegroundColor Red
    exit 1
}

# Step 7: Wait for function to be ready
Write-Host "`n[7/8] Waiting for function update..." -ForegroundColor Yellow
Write-Host "      This may take 30-60 seconds..." -ForegroundColor Gray

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $status = aws lambda get-function-configuration `
        --function-name $FUNCTION_NAME `
        --region $AWS_REGION `
        --query "LastUpdateStatus" `
        --output text 2>&1

    if ($status -eq "Successful") {
        Write-Host "      Function ready!" -ForegroundColor Green
        break
    } elseif ($status -eq "Failed") {
        Write-Host "      ERROR: Function update failed" -ForegroundColor Red
        exit 1
    }

    $attempt++
    Write-Host "      Status: $status (attempt $attempt/$maxAttempts)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

if ($attempt -ge $maxAttempts) {
    Write-Host "      WARNING: Timeout waiting for function" -ForegroundColor Yellow
}

# Step 8: Verify deployment
Write-Host "`n[8/8] Verifying deployment..." -ForegroundColor Yellow

try {
    $config = aws lambda get-function-configuration `
        --function-name $FUNCTION_NAME `
        --region $AWS_REGION `
        --output json | ConvertFrom-Json

    Write-Host "      Runtime: $($config.Runtime)" -ForegroundColor Green
    Write-Host "      Memory: $($config.MemorySize) MB" -ForegroundColor Green
    Write-Host "      Timeout: $($config.Timeout) seconds" -ForegroundColor Green
    Write-Host "      Handler: $($config.Handler)" -ForegroundColor Green

    $envVars = $config.Environment.Variables
    Write-Host "      Environment variables: $($envVars.PSObject.Properties.Name.Count) configured" -ForegroundColor Green

} catch {
    Write-Host "      WARNING: Could not verify configuration" -ForegroundColor Yellow
}

# Final summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Function:        $FUNCTION_NAME" -ForegroundColor White
Write-Host "Region:          $AWS_REGION" -ForegroundColor White
Write-Host "Package size:    $sizeMB MB" -ForegroundColor White
Write-Host "Status:          SUCCESS" -ForegroundColor Green

Write-Host "`nAPI Endpoint:" -ForegroundColor Green
Write-Host "https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod" -ForegroundColor Cyan

Write-Host "`nUpdated routes:" -ForegroundColor Green
Write-Host "  POST /api/auth/login" -ForegroundColor White
Write-Host "  POST /api/auth/signup" -ForegroundColor White
Write-Host "  POST /api/projects/crawl" -ForegroundColor White
Write-Host "  POST /api/projects/translate" -ForegroundColor White
Write-Host "  POST /api/projects/export/{project_id}" -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Test endpoints with curl or Postman" -ForegroundColor White
Write-Host "2. Monitor logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow" -ForegroundColor White
Write-Host "3. Update frontend to use new endpoints" -ForegroundColor White

Write-Host "========================================`n" -ForegroundColor Cyan

exit 0

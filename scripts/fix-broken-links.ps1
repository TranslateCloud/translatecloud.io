# ============================================================================
# Fix Broken Navigation Links
# ============================================================================
# Fixes all logo and language switcher links across EN and ES pages
# href="/en/" → href="/en/index.html"
# href="/es/" → href="/es/index.html"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "FIX BROKEN NAVIGATION LINKS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$fixedCount = 0

# ============================================================================
# Fix English pages
# ============================================================================
Write-Host "[1/2] Fixing English pages..." -ForegroundColor Yellow

Get-ChildItem -Path "frontend/public/en" -Filter "*.html" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    $original = $content

    # Fix logo links
    $content = $content -replace 'href="/en/"', 'href="/en/index.html"'

    # Fix language switcher links
    $content = $content -replace 'href="/es/"', 'href="/es/index.html"'

    if ($content -ne $original) {
        Set-Content $_.FullName $content -Encoding UTF8 -NoNewline
        Write-Host "  ✅ Fixed: $($_.Name)" -ForegroundColor Green
        $fixedCount++
    }
}

# ============================================================================
# Fix Spanish pages
# ============================================================================
Write-Host "`n[2/2] Fixing Spanish pages..." -ForegroundColor Yellow

Get-ChildItem -Path "frontend/public/es" -Filter "*.html" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    $original = $content

    # Fix logo links
    $content = $content -replace 'href="/es/"', 'href="/es/index.html"'

    # Fix language switcher links
    $content = $content -replace 'href="/en/"', 'href="/en/index.html"'

    if ($content -ne $original) {
        Set-Content $_.FullName $content -Encoding UTF8 -NoNewline
        Write-Host "  ✅ Fixed: $($_.Name)" -ForegroundColor Green
        $fixedCount++
    }
}

# ============================================================================
# Summary
# ============================================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "LINK FIXES COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Files Fixed: $fixedCount" -ForegroundColor White
Write-Host "`n✅ All logo and language switcher links updated!`n" -ForegroundColor Green

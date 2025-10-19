#!/usr/bin/env pwsh
# Generate all priority pages for TranslateCloud

Write-Host "Generating priority pages..." -ForegroundColor Cyan

$pages = @{
    "en/about" = @{
        title = "About Us | TranslateCloud"
        heading = "Building the future of website translation"
        description = "Learn about TranslateCloud's mission to make professional website translation accessible to businesses worldwide."
    }
    "en/contact" = @{
        title = "Contact Sales | TranslateCloud"
        heading = "Get in touch with our team"
        description = "Talk to our sales team about enterprise translation solutions for your business."
    }
    "en/features" = @{
        title = "Features | TranslateCloud"
        heading = "Powerful features for global growth"
        description = "Explore all the features that make TranslateCloud the leading enterprise translation platform."
    }
    "en/solutions" = @{
        title = "Solutions | TranslateCloud"
        heading = "Translation solutions for every industry"
        description = "Discover how TranslateCloud helps businesses in different industries expand globally."
    }
    "en/enterprise" = @{
        title = "Enterprise | TranslateCloud"
        heading = "Enterprise-grade translation infrastructure"
        description = "Scalable, secure, and compliant translation solutions for Fortune 500 companies."
    }
    "en/documentation" = @{
        title = "Documentation | TranslateCloud"
        heading = "Documentation & Guides"
        description = "Complete documentation, API references, and integration guides for TranslateCloud."
    }
    "en/help" = @{
        title = "Help Center | TranslateCloud"
        heading = "How can we help you?"
        description = "Find answers to common questions and get support for your TranslateCloud account."
    }
    "en/faq" = @{
        title = "FAQ | TranslateCloud"
        heading = "Frequently Asked Questions"
        description = "Get answers to the most common questions about TranslateCloud."
    }
    "en/api-docs" = @{
        title = "API Documentation | TranslateCloud"
        heading = "TranslateCloud API"
        description = "Complete API reference and integration documentation for developers."
    }
}

foreach ($page in $pages.Keys) {
    $info = $pages[$page]
    $filePath = "frontend/public/$page.html"

    Write-Host "Creating $filePath..." -ForegroundColor Yellow

    $content = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$($info.title)</title>
    <meta name="description" content="$($info.description)">
    <link rel="icon" type="image/svg+xml" href="/assets/images/favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'IBM Plex Sans', sans-serif; line-height: 1.6; color: #111827; }
        .header { background: white; border-bottom: 1px solid #E5E7EB; padding: 1rem 2rem; position: sticky; top: 0; z-index: 1000; }
        .header-container { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.125rem; font-weight: 500; color: #111827; text-decoration: none; display: flex; align-items: center; gap: 0.5rem; }
        .nav { display: flex; gap: 2rem; align-items: center; }
        .nav-link { color: #6B7280; text-decoration: none; font-size: 0.875rem; transition: color 0.15s; }
        .nav-link:hover { color: #111827; }
        .btn-primary { padding: 0.5rem 1rem; background: #111827; color: white; border-radius: 0.375rem; text-decoration: none; font-size: 0.875rem; font-weight: 500; }
        .hero { background: #F9FAFB; padding: 6rem 2rem; text-align: center; }
        .hero-title { font-size: 2.25rem; font-weight: 300; margin-bottom: 1.5rem; }
        .hero-description { font-size: 1.125rem; color: #4B5563; max-width: 800px; margin: 0 auto; }
        .section { padding: 5rem 2rem; max-width: 1400px; margin: 0 auto; }
        .section-title { font-size: 1.875rem; font-weight: 300; margin-bottom: 3rem; text-align: center; }
        .content { font-size: 1rem; color: #374151; line-height: 1.7; }
        .footer { background: #111827; color: #9CA3AF; padding: 3rem 2rem; text-align: center; }
        @media (max-width: 768px) { .hero { padding: 4rem 1.5rem; } .hero-title { font-size: 1.875rem; } }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-container">
            <a href="/en/" class="logo"><i data-lucide="globe" style="width:24px;height:24px;"></i> TranslateCloud</a>
            <nav class="nav">
                <a href="/en/" class="nav-link">Home</a>
                <a href="/en/features.html" class="nav-link">Features</a>
                <a href="/en/pricing.html" class="nav-link">Pricing</a>
                <a href="/en/about.html" class="nav-link">About</a>
                <a href="/en/login.html" class="btn-primary">Sign In</a>
            </nav>
        </div>
    </header>
    <section class="hero">
        <h1 class="hero-title">$($info.heading)</h1>
        <p class="hero-description">$($info.description)</p>
    </section>
    <section class="section">
        <div class="content">
            <p>This page is under construction. Please check back soon for more information.</p>
        </div>
    </section>
    <footer class="footer">
        <p>© 2025 TranslateCloud. All rights reserved.</p>
    </footer>
    <script src="../assets/js/cookies.js"></script>
    <script src="../assets/js/dark-mode.js"></script>
    <script>lucide.createIcons();</script>
</body>
</html>
"@

    $content | Out-File -FilePath $filePath -Encoding UTF8 -NoNewline
}

Write-Host "`nAll pages generated successfully!" -ForegroundColor Green
Write-Host "Total pages created: $($pages.Count)" -ForegroundColor Cyan

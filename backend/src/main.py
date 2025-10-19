from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import projects, translations, users, auth, payments
from src.config.settings import settings
from src.core.translation_service import TranslationService

app = FastAPI(
    title="TranslateCloud API",
    description="AI-powered website translation platform",
    version="1.0.0"
)

# Initialize translation service (DeepL + MarianMT fallback)
translation_service = TranslationService(deepl_api_key=settings.DEEPL_API_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://translatecloud.io",
        "https://www.translatecloud.io",
        "https://translate.translatecloud.io",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://translatecloud-frontend-prod.s3-website-eu-west-1.amazonaws.com",
        "https://translatecloud-frontend-prod.s3-website-eu-west-1.amazonaws.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(translations.router, prefix="/api/translations", tags=["Translations"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

@app.get("/")
async def root():
    return {"message": "TranslateCloud API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/translation/status")
async def get_translation_status():
    """Get translation service status and provider availability"""
    status = translation_service.get_status()
    return {
        "deepl_available": status['deepl_available'],
        "marian_available": status['marian_available'],
        "primary_provider": status['primary_provider'],
        "status": "operational" if status['primary_provider'] else "degraded"
    }

@app.get("/api/translation/usage")
async def get_translation_usage():
    """Get DeepL API usage statistics (if available)"""
    usage = translation_service.get_deepl_usage()

    if usage:
        return {
            "provider": "deepl",
            "characters_used": usage['character_count'],
            "characters_limit": usage['character_limit'],
            "percentage_used": usage['percentage_used'],
            "available": True
        }
    else:
        return {
            "provider": "marian",
            "message": "DeepL not configured - using MarianMT fallback",
            "available": False
        }
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import projects, translations, users, auth, payments, jobs
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TranslateCloud API",
    description="AI-powered website translation platform",
    version="1.0.0"
)

# Initialize translation service lazily on first request
translation_service = None

def get_translation_service():
    """Lazy initialization of translation service"""
    global translation_service
    if translation_service is None:
        from src.core.translation_service import TranslationService

        # Use DeepL API key from environment variable (Lambda env or .env file)
        deepl_key = settings.DEEPL_API_KEY
        if deepl_key:
            logger.info(f"DeepL API key configured: {deepl_key[:8]}...")
        else:
            logger.warning("DeepL API key not configured - translation service will use fallback only")

        translation_service = TranslationService(deepl_api_key=deepl_key)
        logger.info("Translation service initialized successfully")

    return translation_service

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
app.include_router(jobs.router, tags=["Jobs"])

@app.get("/")
async def root():
    return {"message": "TranslateCloud API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/translation/status")
async def get_translation_status():
    """Get translation service status and provider availability"""
    service = get_translation_service()
    status = service.get_status()
    return {
        "deepl_available": status['deepl_available'],
        "marian_available": status['marian_available'],
        "primary_provider": status['primary_provider'],
        "status": "operational" if status['primary_provider'] else "degraded"
    }

@app.get("/api/translation/usage")
async def get_translation_usage():
    """Get DeepL API usage statistics (if available)"""
    service = get_translation_service()
    usage = service.get_deepl_usage()

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
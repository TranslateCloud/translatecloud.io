from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import projects, translations, users, auth
from src.config.settings import settings

app = FastAPI(
    title="TranslateCloud API",
    description="AI-powered website translation platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://translatecloud.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(translations.router, prefix="/api/translations", tags=["Translations"])

@app.get("/")
async def root():
    return {"message": "TranslateCloud API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
"""
Fichier principal des routes API
Pour lancer l'API : 
    -> Se positionner sur eventry/backend
        -> Si UV : uv run python -m uvicorn src.main:app
        -> Si Pyhton : python -m uvicorn src.main:app

    -> Se rendre à l'adresse http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from config import settings
from src.routes import auth, users, events, registration, reviews

# App configuration
app = FastAPI(
    title="Eventry API",
    description="Find Event Anywhere and Enjoy Yourself",
    version="1.0.0",
    docs_url="/docs"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    """Redirige automatiquement vers la documentation Swagger"""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Heath"])
def check_app_statut():
    return{
        "statut" : "application is running"
    }

# Router injection
app.include_router(auth.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(registration.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")
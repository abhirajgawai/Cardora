"""Cardora API entry point."""

import logging
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.features.auth import auth_router, users_router
from app.features.cards.router import router as cards_router
from app.features.categories.router import router as categories_router
from app.features.statements.router import router as statements_router
from app.features.transactions.router import router as transactions_router
from app.features.analytics.router import router as analytics_router
from app.features.insights.router import router as insights_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cardora API",
    description="Credit Card Statement Analyzer with AI-Powered PDF Extraction",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
_dev_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://[::1]:3000",
    "http://[::1]:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_dev_origins if settings.DEBUG else [settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,
)

# ---------------------------------------------------------------------------
# Global exception handler — never expose raw tracebacks
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(cards_router)
app.include_router(categories_router)
app.include_router(statements_router)
app.include_router(transactions_router)
app.include_router(analytics_router)
app.include_router(insights_router)


# ---------------------------------------------------------------------------
# Health / root
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to Cardora API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Cardora API"}

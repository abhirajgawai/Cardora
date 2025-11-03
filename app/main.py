# FastAPI application entry point
# This is similar to Program.cs in ASP.NET Core
# Updated: Added CORS support for IPv6 localhost

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()  # IMPORTANT: Must be called before importing app modules that use env vars

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from new feature-based structure
from app.features.auth import auth_router, users_router
from app.features.cards.router import router as cards_router
from app.features.categories.router import router as categories_router
from app.features.statements.router import router as statements_router
from app.features.transactions.router import router as transactions_router
from app.features.analytics.router import router as analytics_router
from app.features.insights.router import router as insights_router

# Create the FastAPI application instance
# Similar to: var app = WebApplication.CreateBuilder(args).Build();
app = FastAPI(
    title="Cardora API",
    description="Credit Card Statement Analyzer with AI-Powered PDF Extraction",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
# Allow requests from localhost:3000 (Next.js dev server)
# IMPORTANT: This must be added BEFORE registering routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "http://localhost:3001",  # Next.js development server (alternative port)
        "http://127.0.0.1:3000",  # Alternative localhost (IPv4)
        "http://127.0.0.1:3001",  # Alternative localhost (IPv4, port 3001)
        "http://[::1]:3000",      # IPv6 localhost
        "http://[::1]:3001",      # IPv6 localhost (port 3001)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers (Authorization, Content-Type, etc.)
    expose_headers=["*"],  # Expose all headers to the browser
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Register routers (like app.MapControllers() in .NET)
# Compare to .NET: app.MapControllerRoute(...)

# Authentication & Users
app.include_router(auth_router)
app.include_router(users_router)

# Feature 3: AI-Powered Statement Upload
app.include_router(cards_router)  # Manage credit cards
app.include_router(categories_router)  # Transaction categories
app.include_router(statements_router)  # PDF upload & extraction (MAIN FEATURE)
app.include_router(transactions_router)  # View & manage transactions

# Analytics - The Real Value!
app.include_router(analytics_router)  # Spending analysis across cards and time

# AI Insights - The WOW Factor!
app.include_router(insights_router)  # AI-generated and rule-based spending insights

# Payment Alerts - Financial Wellness Feature!
# app.include_router(alerts.router)  # Payment behavior alerts and debt warnings - Disabled for now

# Root endpoint - GET /
# The @app.get() decorator is like [HttpGet("/")] attribute in C#
@app.get("/")
def root():
    """
    Root endpoint - returns a welcome message

    In C# this would be:
    [HttpGet("/")]
    public IActionResult Root()
    {
        return Ok(new { message = "Welcome to Cardora API" });
    }
    """
    return {
        "message": "Welcome to Cardora API",
        "version": "1.0.0"
    }

# Health check endpoint - GET /health
@app.get("/health")
def health_check():
    """
    Health check endpoint
    Returns the API status
    """
    return {
        "status": "healthy",
        "service": "Cardora API"
    }

# Global OPTIONS handler for CORS preflight requests
# This is needed because FastAPI's CORSMiddleware doesn't always handle OPTIONS correctly
# COMMENTED OUT: This was interfering with GET routes on /insights
# The CORSMiddleware is sufficient for handling CORS
# @app.options("/{full_path:path}")
# async def options_handler():
#     """
#     Handle OPTIONS requests for CORS preflight
#     The CORSMiddleware should handle this, but this is a fallback
#     """
#     return {}


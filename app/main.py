# FastAPI application entry point
# This is similar to Program.cs in ASP.NET Core

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, credit_cards, categories, statements, transactions, analytics

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
        "http://127.0.0.1:3000",  # Alternative localhost
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
app.include_router(auth.router)
app.include_router(users.router)

# Feature 3: AI-Powered Statement Upload
app.include_router(credit_cards.router)  # Manage credit cards
app.include_router(categories.router)  # Transaction categories
app.include_router(statements.router)  # PDF upload & extraction (MAIN FEATURE)
app.include_router(transactions.router)  # View & manage transactions

# Analytics - The Real Value!
app.include_router(analytics.router)  # Spending analysis across cards and time

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
@app.options("/{full_path:path}")
async def options_handler():
    """
    Handle OPTIONS requests for CORS preflight
    The CORSMiddleware should handle this, but this is a fallback
    """
    return {}
